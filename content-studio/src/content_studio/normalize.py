"""Brique 1 : normalisation des rushs.

Les rushs peuvent arriver dans n'importe quel format/résolution/orientation
(vertical téléphone, paysage, 4K, 1080p...). Cette brique les ramène tous à un
format "proxy" standard et unique (résolution/fps/codec définis dans
`configs/global.yaml`), pour que toute la suite du pipeline (sous-titres,
overlays, transitions, concat) travaille sur des flux homogènes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from . import ffmpeg_utils as ff
from .models import VideoConfig

Mode = Literal["cover", "contain_blur"]


def build_filter_complex(video_cfg: VideoConfig, mode: Mode) -> str:
    """Construit le graphe de filtres vidéo (entrée `[0:v]`, sortie `[vout]`).

    - "cover" : on remplit tout le cadre vertical en recadrant (peut couper
      les bords d'un rush paysage). Bon défaut pour du contenu déjà filmé
      vertical ou presque.
    - "contain_blur" : on garde l'intégralité du plan (rien de coupé), posé
      sur un fond flouté agrandi. Utile pour un rush paysage qu'on ne veut
      pas rogner (ex: capture d'écran, extrait large).
    """
    w, h = video_cfg.largeur, video_cfg.hauteur
    if mode == "cover":
        return (
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},fps={video_cfg.fps},setsar=1[vout]"
        )
    if mode == "contain_blur":
        return (
            f"[0:v]split=2[bg][fg];"
            f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},gblur=sigma=20[bg2];"
            f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fg2];"
            f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2,fps={video_cfg.fps},setsar=1[vout]"
        )
    raise ValueError(f"mode de normalisation inconnu : {mode!r}")


def normalize_clip(
    input_path: str | Path,
    output_path: str | Path,
    video_cfg: VideoConfig,
    mode: Mode = "cover",
    start: Optional[float] = None,
    end: Optional[float] = None,
) -> Path:
    """Normalise un rush vers le format proxy standard (résolution/fps/codec).

    `start`/`end` (en secondes) découpent le rush avant normalisation.
    Si le rush n'a pas de piste audio, une piste silencieuse est ajoutée pour
    garder des flux homogènes (indispensable pour la concat plus tard).
    """
    ff.check_ffmpeg_available()
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    info = ff.probe(input_path)
    filter_str = build_filter_complex(video_cfg, mode)

    cmd = ["ffmpeg", "-y"]
    if start:
        cmd += ["-ss", f"{start}"]
    cmd += ["-i", str(input_path)]

    if info.has_audio:
        audio_map = "0:a"
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        audio_map = "1:a"

    cmd += ["-filter_complex", filter_str, "-map", "[vout]", "-map", audio_map]

    if end is not None:
        duration = end - (start or 0.0)
        cmd += ["-t", f"{duration}"]

    # Indispensable : quand une piste silencieuse (anullsrc) est ajoutée,
    # c'est un générateur audio infini. Sans -shortest (ni -t explicite),
    # ffmpeg ne s'arrêterait jamais puisque l'audio ne finit pas de lui-même.
    cmd += ["-shortest"]

    cmd += [
        "-c:v", video_cfg.codec_video,
        "-crf", str(video_cfg.crf),
        "-preset", video_cfg.preset,
        "-c:a", video_cfg.codec_audio,
        "-b:a", video_cfg.bitrate_audio,
        "-r", str(video_cfg.fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path
