"""Brique 4b : titres animés (cartons d'intro / accroches)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import ffmpeg_utils as ff
from .drawtext import drawtext_filter, hex_to_ffmpeg_color, write_textfile
from .fonts import resolve_font_path
from .models import TitresStyle, VideoConfig

_FADE_S = 0.3
_SLIDE_S = 0.35
_SLIDE_OFFSET_PX = 140


def _alpha_expr(style: TitresStyle, duration_s: float) -> str:
    """Fondu d'entrée/sortie du texte (indépendant de l'animation de fond)."""
    fi = _FADE_S if style.animation_entree in ("fade",) else 0.0
    fo = _FADE_S if style.animation_sortie == "fade" else 0.0
    if fi == 0 and fo == 0:
        return "1"
    expr = "1"
    if fo > 0:
        expr = f"if(gt(t\\,{duration_s}-{fo})\\,({duration_s}-t)/{fo}\\,{expr})"
    if fi > 0:
        expr = f"if(lt(t\\,{fi})\\,t/{fi}\\,{expr})"
    return expr


def _y_expr(style: TitresStyle, base_y: str, duration_s: float) -> str:
    """Position verticale du texte, avec glissement d'entrée/sortie éventuel."""
    expr = base_y
    if style.animation_entree == "slide_up":
        expr = (
            f"if(lt(t\\,{_SLIDE_S})\\,({base_y})+{_SLIDE_OFFSET_PX}*(1-t/{_SLIDE_S})\\,{expr})"
        )
    if style.animation_sortie == "slide_down":
        expr = (
            f"if(gt(t\\,{duration_s}-{_SLIDE_S})\\,"
            f"({base_y})+{_SLIDE_OFFSET_PX}*((t-({duration_s}-{_SLIDE_S}))/{_SLIDE_S})\\,{expr})"
        )
    return expr


def _background_filter(style: TitresStyle, video_cfg: VideoConfig, duration_s: float) -> Optional[str]:
    """Filtre appliqué au fond du carton (avant le texte) ; None si aucun."""
    if style.animation_entree == "zoom":
        w, h, fps = video_cfg.largeur, video_cfg.hauteur, video_cfg.fps
        # zoom progressif léger sur toute la durée du carton
        n_frames = max(int(duration_s * fps), 1)
        return f"zoompan=z='min(zoom+{0.4 / max(n_frames, 1):.6f}\\,1.15)':d=1:s={w}x{h}:fps={fps}"
    return None


def render_title_card(
    text: str,
    style: TitresStyle,
    video_cfg: VideoConfig,
    duration_s: float,
    output_path: str | Path,
    fonts_dir: Optional[Path] = None,
    work_dir: Optional[Path] = None,
) -> Path:
    """Génère un carton de titre autonome (fond plein + texte animé), prêt à
    être mis bout à bout avec les séquences (même format que les rushs
    normalisés : résolution/fps/codec/piste audio silencieuse)."""
    ff.check_ffmpeg_available()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir = Path(work_dir) if work_dir else output_path.parent / ".tmp_titles"
    work_dir.mkdir(parents=True, exist_ok=True)

    font_path = resolve_font_path(style.police, fonts_dir)
    textfile = write_textfile(text, work_dir / f"{output_path.stem}_title.txt")

    base_x = "((w-text_w)/2)"
    base_y = "((h-text_h)/2)"
    y_expr = _y_expr(style, base_y, duration_s)
    alpha_expr = _alpha_expr(style, duration_s)

    dt = drawtext_filter(
        textfile_path=textfile,
        fontfile_path=font_path,
        fontsize=style.taille_px,
        fontcolor=hex_to_ffmpeg_color(style.couleur_texte),
        x=base_x,
        y=y_expr,
        alpha=alpha_expr,
    )

    bg_filter = _background_filter(style, video_cfg, duration_s)
    vf = f"{bg_filter},{dt}" if bg_filter else dt

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={hex_to_ffmpeg_color(style.couleur_fond)}:size={video_cfg.largeur}x{video_cfg.hauteur}:duration={duration_s}:rate={video_cfg.fps}",
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000",
        "-vf", vf,
        "-shortest",
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", video_cfg.codec_audio, "-b:a", video_cfg.bitrate_audio,
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path


def apply_title_overlay(
    input_video: str | Path,
    output_video: str | Path,
    text: str,
    style: TitresStyle,
    video_cfg: VideoConfig,
    start_s: float,
    duration_s: float,
    fonts_dir: Optional[Path] = None,
    work_dir: Optional[Path] = None,
) -> Path:
    """Variante "overlay_transparent" : pose le titre par-dessus un rush
    existant (au lieu d'un carton plein séparé), actif entre start_s et
    start_s+duration_s."""
    ff.check_ffmpeg_available()
    input_video, output_video = Path(input_video), Path(output_video)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    work_dir = Path(work_dir) if work_dir else output_video.parent / ".tmp_titles"

    font_path = resolve_font_path(style.police, fonts_dir)
    textfile = write_textfile(text, work_dir / f"{output_video.stem}_title.txt")

    end_s = start_s + duration_s
    dt = drawtext_filter(
        textfile_path=textfile,
        fontfile_path=font_path,
        fontsize=style.taille_px,
        fontcolor=hex_to_ffmpeg_color(style.couleur_texte),
        x="((w-text_w)/2)",
        y="((h-text_h)/2)",
        borderw=3,
        bordercolor="0x000000",
        enable=f"between(t\\,{start_s}\\,{end_s})",
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(input_video),
        "-vf", dt,
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_video),
    ]
    ff.run(cmd)
    return output_video
