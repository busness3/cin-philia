"""Orchestrateur : assemble toutes les briques pour rendre un épisode complet
à partir de `episodes/*.yaml` + la config de la série concernée.

v2 — aligné sur le document de DA globale « petit boucan » : plus de carton
d'intro séparé, le titre est incrusté sur le plan d'ouverture (bandeau
crème + bloc accent) ; sortie optionnelle avec le même bandeau + CTA de la
série ; musique opt-in par épisode (pas de musique par défaut), qui démarre
après le premier mot détecté par la transcription quand elle est présente.
Pas de génération automatique de couverture (Cléa s'en charge elle-même).

Étapes, par séquence : normalisation (recadrage/format proxy) -> sous-titres
(auto/SRT fourni/aucun) -> overlays texte ponctuels. Puis assemblage des
séquences avec transitions, bandeau d'ouverture, bandeau de sortie (si
activé et demandé), mixage audio (voix + musique optionnelle + SFX). Le
tout dans un dossier de travail temporaire, nettoyé à la fin sauf si
`keep_intermediates=True`.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Optional

from . import audio as audio_mod
from . import band as band_mod
from . import ffmpeg_utils as ff
from . import overlays as overlays_mod
from . import subtitles as subtitles_mod
from . import transcribe as transcribe_mod
from . import transitions as transitions_mod
from .config import ASSETS_DIR, ROOT, SOUNDS_DIR, load_episode, resolve_config
from .fonts import resolve_font_path
from .models import EpisodeConfig, ResolvedConfig, SfxCue
from .normalize import normalize_clip
from .sound_library import SoundLibraryError, get_sfx, pick_music


def _log(msg: str) -> None:
    print(f"[pipeline] {msg}", file=sys.stderr)


def _resolve_rush_path(rush: str) -> Path:
    p = Path(rush)
    if p.is_absolute():
        return p
    candidate = ROOT / p
    return candidate if candidate.exists() else p


def _default_overlay_style(resolved: ResolvedConfig) -> dict:
    st = resolved.global_.sous_titres
    return dict(
        police=st.police,
        taille_px=max(int(st.taille_px * 0.7), 24),
        couleur_texte=st.couleur_texte,
        couleur_contour="#000000",
        epaisseur_contour=0,  # style minimaliste de la DA : pas de contour
    )


def _render_sequence(
    seq,
    index: int,
    resolved: ResolvedConfig,
    work_dir: Path,
    fonts_dir: Path,
) -> tuple[Path, Optional[float]]:
    """Rend une séquence (normalisation + sous-titres + overlays).

    Renvoie (clip, premier_mot_s) — `premier_mot_s` est l'instant du premier
    mot détecté par la transcription auto (utile pour caler le départ de la
    musique sur la 1re séquence), ou None si non déterminé.
    """
    video_cfg = resolved.global_.video
    sous_titres_cfg = resolved.global_.sous_titres
    rush_path = _resolve_rush_path(seq.rush)

    normalized = normalize_clip(
        rush_path, work_dir / f"seq{index:02d}_norm.mp4", video_cfg,
        mode="cover", start=seq.debut_s or None, end=seq.fin_s,
    )
    current = normalized
    premier_mot_s: Optional[float] = None

    if seq.sous_titres == "auto":
        try:
            result = transcribe_mod.transcribe(current, language="fr")
        except Exception as e:  # modèle indisponible, audio illisible, etc.
            _log(f"séquence {index} : transcription auto indisponible ({e}) -> pas de sous-titres")
            result = None
        if result and result.words:
            premier_mot_s = result.words[0].start
        if result and (result.words or result.segments):
            ass_content = subtitles_mod.build_ass(
                sous_titres_cfg, video_cfg, words=result.words, segments=result.segments
            )
            ass_path = subtitles_mod.write_ass(ass_content, work_dir / f"seq{index:02d}_subs.ass")
            current = subtitles_mod.burn_subtitles(
                current, ass_path, work_dir / f"seq{index:02d}_subs.mp4", video_cfg, fonts_dir=fonts_dir
            )
    elif seq.sous_titres != "aucun":
        # chemin vers un .srt fourni par Cléa
        srt_path = _resolve_rush_path(seq.sous_titres)
        groups = transcribe_mod.parse_srt(srt_path)
        if groups:
            premier_mot_s = groups[0].start
            ass_content = subtitles_mod.build_ass_from_groups(groups, sous_titres_cfg, video_cfg)
            ass_path = subtitles_mod.write_ass(ass_content, work_dir / f"seq{index:02d}_subs.ass")
            current = subtitles_mod.burn_subtitles(
                current, ass_path, work_dir / f"seq{index:02d}_subs.mp4", video_cfg, fonts_dir=fonts_dir
            )

    if seq.overlay_texte:
        style = _default_overlay_style(resolved)
        current = overlays_mod.apply_text_overlays(
            current, work_dir / f"seq{index:02d}_overlay.mp4", seq.overlay_texte, video_cfg,
            fonts_dir=fonts_dir, work_dir=work_dir, **style,
        )

    return current, premier_mot_s


def render_episode(
    episode_path: str | Path,
    work_dir: Optional[Path] = None,
    keep_intermediates: bool = False,
) -> Path:
    episode: EpisodeConfig = load_episode(episode_path)
    resolved = resolve_config(episode.serie)
    video_cfg = resolved.global_.video
    timing = resolved.global_.timing
    fonts_dir = ASSETS_DIR / "fonts"
    titre_font_path = resolve_font_path(resolved.global_.fonts.titre.police, fonts_dir)

    work_dir = Path(work_dir) if work_dir else ROOT / "out" / f".tmp_{Path(episode.sortie).stem}"
    work_dir.mkdir(parents=True, exist_ok=True)
    _log(f"dossier de travail : {work_dir}")

    clips: list[Path] = []
    transitions: list[str] = []
    default_trans = resolved.global_.rythme.transition_defaut
    premier_mot_s: Optional[float] = None

    for i, seq in enumerate(episode.sequences):
        _log(f"séquence {i + 1}/{len(episode.sequences)} : {seq.rush}")
        clip, first_word = _render_sequence(seq, i, resolved, work_dir, fonts_dir)
        if i == 0 and first_word is not None:
            premier_mot_s = first_word
        clips.append(clip)
        if i < len(episode.sequences) - 1:
            transitions.append(seq.transition_sortie or default_trans)

    _log(f"assemblage de {len(clips)} clip(s) avec transitions")
    assembled = transitions_mod.concat_with_transitions(
        clips, transitions, resolved.global_.rythme.duree_transition_ms / 1000,
        work_dir / "assembled.mp4", video_cfg,
    )
    current = assembled

    if episode.accroche and episode.accroche.texte:
        _log("incrustation du titre d'ouverture (bandeau)")
        current = band_mod.apply_band_to_video(
            current, work_dir / "with_open_band.mp4", resolved.global_.couverture,
            resolved.serie.accent, titre_font_path, resolved.global_.fonts.titre.taille_px,
            episode.accroche.texte, video_cfg,
            start_s=timing.titre_apparition_s, duration_s=timing.titre_duree_s,
            work_dir=work_dir, label_prefix="ouverture",
        )

    if timing.sortie_activee and resolved.serie.cta_sortie:
        total_duration = ff.probe(current).duration
        outro_start = max(total_duration - timing.sortie_duree_s, 0.0)
        _log("incrustation du bandeau de sortie (CTA)")
        current = band_mod.apply_band_to_video(
            current, work_dir / "with_outro_band.mp4", resolved.global_.couverture,
            resolved.serie.accent, titre_font_path, resolved.global_.fonts.titre.taille_px,
            resolved.serie.cta_sortie, video_cfg,
            start_s=outro_start, duration_s=timing.sortie_duree_s,
            work_dir=work_dir, label_prefix="sortie",
        )

    if resolved.global_.identite.watermark.actif and resolved.global_.identite.watermark.image:
        _log("application du watermark global (logo)")
        current = overlays_mod.apply_image_watermark(
            current, work_dir / "with_wm_global.mp4", resolved.global_.identite.watermark, video_cfg
        )

    duration_s = ff.probe(current).duration

    # Musique opt-in : pas de musique par défaut (toutes les vidéos n'en ont
    # pas besoin). Ajoutée uniquement si l'épisode la demande explicitement
    # (chemin précis, ou mood pioché dans la bibliothèque pour CETTE vidéo).
    music_path = None
    if episode.audio.musique:
        music_path = _resolve_rush_path(episode.audio.musique)
    elif episode.audio.mood_musique:
        try:
            music_path = pick_music(episode.audio.mood_musique, SOUNDS_DIR)
        except SoundLibraryError as e:
            _log(f"pas de musique : {e}")

    music_delay_s = 0.0
    if timing.musique_apres_voix and music_path is not None:
        music_delay_s = premier_mot_s if premier_mot_s is not None else 1.0

    sfx_paths: dict[str, Path] = {}
    sfx_cues: list[SfxCue] = []
    for cue in episode.audio.sfx:
        try:
            sfx_paths[cue.id] = get_sfx(cue.id, SOUNDS_DIR)
            sfx_cues.append(cue)
        except SoundLibraryError as e:
            _log(f"sfx ignoré : {e}")

    _log(f"mixage audio (musique{' (délai ' + str(round(music_delay_s, 2)) + 's)' if music_delay_s else ''} + sfx + voix)")
    final = audio_mod.mix_audio(
        current, work_dir / "final.mp4", video_cfg, duration_s,
        music_path=music_path,
        music_volume_db=resolved.serie.audio.volume_musique_db,
        sfx_cues=sfx_cues, sfx_paths=sfx_paths,
        sfx_default_volume_db=resolved.global_.audio.sfx.volume_defaut_db,
        loudness_lufs=resolved.global_.audio.loudness_cible_lufs,
        music_delay_s=music_delay_s,
    )

    sortie = Path(episode.sortie)
    if not sortie.is_absolute():
        sortie = ROOT / sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, sortie)
    _log(f"terminé : {sortie}")

    # Pas de génération automatique de couverture : Cléa s'en occupe
    # elle-même (cf. cover.py, dispo si un usage manuel/futur le demande).

    if not keep_intermediates:
        shutil.rmtree(work_dir, ignore_errors=True)
    else:
        _log(f"fichiers intermédiaires conservés dans {work_dir}")

    return sortie
