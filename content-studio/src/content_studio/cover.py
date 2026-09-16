"""Générateur de couverture — image fixe 1080×1920 pour la vignette TikTok.

Extrait une frame de la vidéo (idéalement le visage visible) et y applique le
même gabarit bandeau/bloc accent/titre que le bandeau incrusté en vidéo — la
couverture et l'ouverture de la vidéo se répondent visuellement.
"""
from __future__ import annotations

from pathlib import Path

from . import ffmpeg_utils as ff
from .band import band_filters
from .models import GabaritCouverture, VideoConfig


def generate_cover(
    video_path: str | Path,
    output_path: str | Path,
    gabarit: GabaritCouverture,
    accent_hex: str,
    titre_font_path: str | Path,
    titre_taille_px: int,
    texte: str,
    video_cfg: VideoConfig,
    temps_capture_s: float,
    work_dir: str | Path,
) -> Path:
    """Génère la couverture PNG : frame extraite à `temps_capture_s` + bandeau
    titre superposé (toujours visible, pas de fenêtre temporelle)."""
    ff.check_ffmpeg_available()
    video_path, output_path = Path(video_path), Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filters = band_filters(
        gabarit, accent_hex, titre_font_path, titre_taille_px, texte,
        work_dir, "couverture", enable_expr=None,
    )
    vf = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{temps_capture_s}",
        "-i", str(video_path),
        "-vf", vf,
        "-frames:v", "1", "-update", "1",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path
