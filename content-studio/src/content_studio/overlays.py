"""Brique 4a : overlays (texte ponctuel, cadre, watermark image/texte)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import ffmpeg_utils as ff
from .drawtext import drawtext_filter, escape_filter_path, hex_to_ffmpeg_color, write_textfile
from .fonts import resolve_font_path
from .models import CadreOverlay, VideoConfig, Watermark, WatermarkSerie

Position = str  # "haut_gauche" | "haut_centre" | "haut_droite" | "centre" | "bas_gauche" | "bas_centre" | "bas_droite"


def position_expr(
    position: Position,
    video_cfg: VideoConfig,
    total_w: str = "w",
    total_h: str = "h",
    elem_w: str = "text_w",
    elem_h: str = "text_h",
) -> tuple[str, str]:
    """(x_expr, y_expr) pour placer un élément selon une position nommée,
    en respectant la zone sûre (hors UI TikTok) définie dans la config globale.

    `total_w/h` et `elem_w/h` sont les noms de variables ffmpeg à utiliser
    (différents entre `drawtext` : w/h + text_w/text_h, et `overlay` : W/H + w/h).
    """
    mx = video_cfg.zone_sure.lateral_px
    top = video_cfg.zone_sure.haut_px
    bottom = video_cfg.zone_sure.bas_px

    x_left = str(mx)
    x_right = f"({total_w}-{elem_w}-{mx})"
    x_center = f"(({total_w}-{elem_w})/2)"
    y_top = str(top)
    y_bottom = f"({total_h}-{elem_h}-{bottom})"
    y_center = f"(({total_h}-{elem_h})/2)"

    mapping: dict[str, tuple[str, str]] = {
        "haut_gauche": (x_left, y_top),
        "haut_centre": (x_center, y_top),
        "haut_droite": (x_right, y_top),
        "centre": (x_center, y_center),
        "bas_gauche": (x_left, y_bottom),
        "bas_centre": (x_center, y_bottom),
        "bas_droite": (x_right, y_bottom),
    }
    if position not in mapping:
        raise ValueError(f"position inconnue : {position!r}")
    return mapping[position]


def apply_text_overlays(
    input_video: str | Path,
    output_video: str | Path,
    overlays: list,  # list[OverlayTexte]
    video_cfg: VideoConfig,
    police: str,
    taille_px: int,
    couleur_texte: str,
    couleur_contour: str = "#000000",
    epaisseur_contour: int = 2,
    fonts_dir: Optional[Path] = None,
    work_dir: Optional[Path] = None,
) -> Path:
    """Incruste une liste d'overlays texte ponctuels (ex: alertes, légendes),
    chacun actif seulement entre son `debut_s` et sa `fin_s`."""
    ff.check_ffmpeg_available()
    input_video, output_video = Path(input_video), Path(output_video)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    work_dir = Path(work_dir) if work_dir else output_video.parent / ".tmp_overlays"
    work_dir.mkdir(parents=True, exist_ok=True)

    if not overlays:
        # rien à faire : simple copie
        cmd = ["ffmpeg", "-y", "-i", str(input_video), "-c", "copy", str(output_video)]
        ff.run(cmd)
        return output_video

    font_path = resolve_font_path(police, fonts_dir)
    filters = []
    for i, ov in enumerate(overlays):
        textfile = write_textfile(ov.texte, work_dir / f"overlay_{i}.txt")
        x, y = position_expr(ov.position, video_cfg)
        filters.append(
            drawtext_filter(
                textfile_path=textfile,
                fontfile_path=font_path,
                fontsize=taille_px,
                fontcolor=hex_to_ffmpeg_color(couleur_texte),
                x=x,
                y=y,
                borderw=epaisseur_contour,
                bordercolor=hex_to_ffmpeg_color(couleur_contour),
                enable=f"between(t\\,{ov.debut_s}\\,{ov.fin_s})",
            )
        )
    vf = ",".join(filters)

    cmd = [
        "ffmpeg", "-y", "-i", str(input_video),
        "-vf", vf,
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_video),
    ]
    ff.run(cmd)
    return output_video


def apply_cadre(
    input_video: str | Path,
    output_video: str | Path,
    cadre: CadreOverlay,
    video_cfg: VideoConfig,
) -> Path:
    """Dessine un cadre (bordure) sur tout le pourtour de l'image."""
    ff.check_ffmpeg_available()
    input_video, output_video = Path(input_video), Path(output_video)
    output_video.parent.mkdir(parents=True, exist_ok=True)

    color = hex_to_ffmpeg_color(cadre.couleur)
    vf = f"drawbox=x=0:y=0:w=iw:h=ih:color={color}:t={cadre.epaisseur_px}"
    cmd = [
        "ffmpeg", "-y", "-i", str(input_video),
        "-vf", vf,
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_video),
    ]
    ff.run(cmd)
    return output_video


def apply_image_watermark(
    input_video: str | Path,
    output_video: str | Path,
    watermark: Watermark,
    video_cfg: VideoConfig,
    largeur_relative: float = 0.16,
) -> Path:
    """Incruste le logo/watermark (image) défini dans la config globale."""
    if not watermark.actif or not watermark.image:
        raise ValueError("watermark inactif ou sans image : rien à faire")
    ff.check_ffmpeg_available()
    input_video, output_video = Path(input_video), Path(output_video)
    output_video.parent.mkdir(parents=True, exist_ok=True)

    target_w = int(video_cfg.largeur * largeur_relative)
    x, y = position_expr(watermark.position, video_cfg, total_w="W", total_h="H", elem_w="w", elem_h="h")

    filter_complex = (
        f"[1:v]scale={target_w}:-1,format=rgba,"
        f"colorchannelmixer=aa={watermark.opacite}[wm];"
        f"[0:v][wm]overlay=x={x}:y={y}[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_video),
        "-i", str(watermark.image),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "0:a",
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_video),
    ]
    ff.run(cmd)
    return output_video


def apply_text_watermark(
    input_video: str | Path,
    output_video: str | Path,
    watermark_serie: WatermarkSerie,
    video_cfg: VideoConfig,
    police: str,
    couleur: str = "#FFFFFF",
    taille_px: int = 34,
    fonts_dir: Optional[Path] = None,
    work_dir: Optional[Path] = None,
) -> Path:
    """Incruste un petit label texte (nom de la série) façon watermark."""
    if not watermark_serie.actif or not watermark_serie.texte:
        raise ValueError("watermark_serie inactif ou sans texte : rien à faire")
    ff.check_ffmpeg_available()
    input_video, output_video = Path(input_video), Path(output_video)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    work_dir = Path(work_dir) if work_dir else output_video.parent / ".tmp_overlays"

    font_path = resolve_font_path(police, fonts_dir)
    textfile = write_textfile(watermark_serie.texte, work_dir / "watermark_serie.txt")
    x, y = position_expr(watermark_serie.position, video_cfg)
    vf = drawtext_filter(
        textfile_path=textfile,
        fontfile_path=font_path,
        fontsize=taille_px,
        fontcolor=hex_to_ffmpeg_color(couleur),
        x=x,
        y=y,
        borderw=2,
        bordercolor="0x000000",
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(input_video),
        "-vf", vf,
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_video),
    ]
    ff.run(cmd)
    return output_video
