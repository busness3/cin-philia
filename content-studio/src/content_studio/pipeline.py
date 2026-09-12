"""Orchestrateur : assemble toutes les briques pour rendre un épisode complet
à partir de `episodes/*.yaml` + la config de la série concernée.

Étapes, par séquence : normalisation (recadrage/format proxy) -> sous-titres
(auto/SRT fourni/aucun) -> overlays texte ponctuels. Puis assemblage de
l'accroche + des séquences avec transitions, cadre/watermarks, et enfin mixage
audio (musique de la bibliothèque + SFX). Le tout dans un dossier de travail
temporaire, nettoyé à la fin sauf si `keep_intermediates=True`.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Optional

from . import audio as audio_mod
from . import ffmpeg_utils as ff
from . import overlays as overlays_mod
from . import subtitles as subtitles_mod
from . import transcribe as transcribe_mod
from . import transitions as transitions_mod
from .config import ASSETS_DIR, EPISODES_DIR, ROOT, SOUNDS_DIR, load_episode, resolve_config
from .models import EpisodeConfig, ResolvedConfig, SfxCue
from .normalize import normalize_clip
from .sound_library import SoundLibraryError, get_sfx, pick_music
from .titles import render_title_card


def _log(msg: str) -> None:
    print(f"[pipeline] {msg}", file=sys.stderr)


def _resolve_rush_path(rush: str) -> Path:
    p = Path(rush)
    if p.is_absolute():
        return p
    # essaie relatif à content-studio/ (ROOT), sinon tel quel (relatif au cwd)
    candidate = ROOT / p
    return candidate if candidate.exists() else p


def _default_overlay_style(resolved: ResolvedConfig) -> dict:
    st = resolved.serie.sous_titres
    return dict(
        police=resolved.serie.titres.police,
        taille_px=max(int(st.taille_px * 0.6), 24),
        couleur_texte=st.couleur_texte,
        couleur_contour=st.couleur_contour,
        epaisseur_contour=max(st.epaisseur_contour - 1, 1),
    )


def _render_sequence(
    seq,
    index: int,
    resolved: ResolvedConfig,
    work_dir: Path,
    fonts_dir: Path,
) -> Path:
    video_cfg = resolved.global_.video
    rush_path = _resolve_rush_path(seq.rush)

    normalized = normalize_clip(
        rush_path, work_dir / f"seq{index:02d}_norm.mp4", video_cfg,
        mode="cover", start=seq.debut_s or None, end=seq.fin_s,
    )
    current = normalized

    if seq.sous_titres == "auto":
        try:
            words = transcribe_mod.transcribe(current, language="fr")
        except Exception as e:  # modèle indisponible, audio illisible, etc.
            _log(f"séquence {index} : transcription auto indisponible ({e}) -> pas de sous-titres")
            words = []
        if words:
            ass_path = subtitles_mod.write_ass(
                words, resolved.serie.sous_titres, video_cfg, work_dir / f"seq{index:02d}_subs.ass"
            )
            current = subtitles_mod.burn_subtitles(
                current, ass_path, work_dir / f"seq{index:02d}_subs.mp4", video_cfg, fonts_dir=fonts_dir
            )
    elif seq.sous_titres != "aucun":
        # chemin vers un .srt fourni par Cléa
        srt_path = _resolve_rush_path(seq.sous_titres)
        groups = transcribe_mod.parse_srt(srt_path)
        words = [g.words[0] for g in groups]
        style_1 = resolved.serie.sous_titres.model_copy(update={"mots_par_groupe": 1})
        ass_path = subtitles_mod.write_ass(words, style_1, video_cfg, work_dir / f"seq{index:02d}_subs.ass")
        current = subtitles_mod.burn_subtitles(
            current, ass_path, work_dir / f"seq{index:02d}_subs.mp4", video_cfg, fonts_dir=fonts_dir
        )

    if seq.overlay_texte:
        style = _default_overlay_style(resolved)
        current = overlays_mod.apply_text_overlays(
            current, work_dir / f"seq{index:02d}_overlay.mp4", seq.overlay_texte, video_cfg,
            fonts_dir=fonts_dir, work_dir=work_dir, **style,
        )

    return current


def render_episode(
    episode_path: str | Path,
    work_dir: Optional[Path] = None,
    keep_intermediates: bool = False,
) -> Path:
    episode: EpisodeConfig = load_episode(episode_path)
    resolved = resolve_config(episode.serie)
    video_cfg = resolved.global_.video
    fonts_dir = ASSETS_DIR / "fonts"

    work_dir = Path(work_dir) if work_dir else ROOT / "out" / f".tmp_{Path(episode.sortie).stem}"
    work_dir.mkdir(parents=True, exist_ok=True)
    _log(f"dossier de travail : {work_dir}")

    clips: list[Path] = []
    transitions: list[str] = []
    default_trans = resolved.serie.rythme.transition_defaut

    if episode.accroche:
        _log("rendu de l'accroche (carton de titre)")
        card = render_title_card(
            episode.accroche.texte, resolved.serie.titres, video_cfg,
            episode.accroche.duree_s, work_dir / "00_accroche.mp4",
            fonts_dir=fonts_dir, work_dir=work_dir,
        )
        clips.append(card)
        transitions.append(default_trans)

    for i, seq in enumerate(episode.sequences):
        _log(f"séquence {i + 1}/{len(episode.sequences)} : {seq.rush}")
        clip = _render_sequence(seq, i, resolved, work_dir, fonts_dir)
        clips.append(clip)
        if i < len(episode.sequences) - 1:
            transitions.append(seq.transition_sortie or default_trans)

    _log(f"assemblage de {len(clips)} clip(s) avec transitions")
    assembled = transitions_mod.concat_with_transitions(
        clips, transitions, resolved.serie.rythme.duree_transition_ms / 1000,
        work_dir / "assembled.mp4", video_cfg,
    )
    current = assembled

    if resolved.serie.overlays.cadre.actif:
        _log("application du cadre")
        current = overlays_mod.apply_cadre(current, work_dir / "with_cadre.mp4", resolved.serie.overlays.cadre, video_cfg)

    if resolved.serie.overlays.watermark_serie.actif:
        _log("application du watermark série")
        current = overlays_mod.apply_text_watermark(
            current, work_dir / "with_wm_serie.mp4", resolved.serie.overlays.watermark_serie, video_cfg,
            police=resolved.global_.identite.police_principale, fonts_dir=fonts_dir, work_dir=work_dir,
        )

    if resolved.global_.identite.watermark.actif and resolved.global_.identite.watermark.image:
        _log("application du watermark global (logo)")
        current = overlays_mod.apply_image_watermark(
            current, work_dir / "with_wm_global.mp4", resolved.global_.identite.watermark, video_cfg
        )

    duration_s = ff.probe(current).duration

    music_path = None
    if episode.audio.musique:
        music_path = _resolve_rush_path(episode.audio.musique)
    elif resolved.serie.audio.mood_musique:
        try:
            music_path = pick_music(resolved.serie.audio.mood_musique, SOUNDS_DIR)
        except SoundLibraryError as e:
            _log(f"pas de musique : {e}")

    sfx_paths: dict[str, Path] = {}
    sfx_cues: list[SfxCue] = []
    for cue in episode.audio.sfx:
        try:
            sfx_paths[cue.id] = get_sfx(cue.id, SOUNDS_DIR)
            sfx_cues.append(cue)
        except SoundLibraryError as e:
            _log(f"sfx ignoré : {e}")

    _log("mixage audio (musique + sfx + voix)")
    final = audio_mod.mix_audio(
        current, work_dir / "final.mp4", video_cfg, duration_s,
        music_path=music_path,
        music_volume_db=resolved.serie.audio.volume_musique_db,
        sfx_cues=sfx_cues, sfx_paths=sfx_paths,
        sfx_default_volume_db=resolved.global_.audio.sfx.volume_defaut_db,
        loudness_lufs=resolved.global_.audio.loudness_cible_lufs,
    )

    sortie = Path(episode.sortie)
    if not sortie.is_absolute():
        sortie = ROOT / sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, sortie)
    _log(f"terminé : {sortie}")

    if not keep_intermediates:
        shutil.rmtree(work_dir, ignore_errors=True)
    else:
        _log(f"fichiers intermédiaires conservés dans {work_dir}")

    return sortie
