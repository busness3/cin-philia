"""Brique 2 : sous-titres synchronisés (génération ASS + burn-in).

Style v2 — texte intégré directement sur l'image (pas de fond), contour
crème pour rester lisible sur n'importe quel plan, pas d'animation, pas de
surlignage mot par mot. Le format .ass (via libass) est utilisé pour un
positionnement pixel-précis (BorderStyle=1 : contour + ombre, ombre à 0).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import ffmpeg_utils as ff
from .models import SousTitresConfig, VideoConfig
from .transcribe import Word, WordGroup, group_words


def hex_to_ass_color(hex_color: str, alpha_hex: str = "00") -> str:
    """Convertit #RRGGBB en couleur ASS &HAABBGGRR& (ordre inversé, alpha en tête)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
    return f"&H{alpha_hex}{b}{g}{r}&".upper()


def _escape_ass_text(text: str) -> str:
    return text.replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


def _style_line(config: SousTitresConfig, video_cfg: VideoConfig) -> str:
    primary = hex_to_ass_color(config.couleur_texte)
    outline = hex_to_ass_color(config.couleur_contour)
    margin_v = video_cfg.hauteur - config.baseline_y_px
    return (
        "Style: sous_titres,"
        f"{config.police},{config.taille_px},{primary},{primary},{outline},&H00000000,"
        f"0,0,0,0,100,100,0,0,1,{config.epaisseur_contour},0,2,"
        f"{video_cfg.zone_sure.lateral_px},{video_cfg.zone_sure.lateral_px},{margin_v},1"
    )


def _script_header(config: SousTitresConfig, video_cfg: VideoConfig) -> str:
    return (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {video_cfg.largeur}\n"
        f"PlayResY: {video_cfg.hauteur}\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"{_style_line(config, video_cfg)}\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )


def _fmt_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs == 100:
        cs = 0
        s += 1
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass_from_groups(groups: list[WordGroup], config: SousTitresConfig, video_cfg: VideoConfig) -> str:
    """Construit le .ass à partir de groupes déjà formés (segments whisper,
    lignes de SRT fourni, ou paquets de mots)."""
    events = []
    for group in groups:
        text = _escape_ass_text(group.text)
        events.append(f"Dialogue: 0,{_fmt_ts(group.start)},{_fmt_ts(group.end)},sous_titres,,0,0,0,,{text}")
    return _script_header(config, video_cfg) + "\n".join(events) + "\n"


def build_ass(
    config: SousTitresConfig,
    video_cfg: VideoConfig,
    words: Optional[list[Word]] = None,
    segments: Optional[list[WordGroup]] = None,
) -> str:
    """Point d'entrée principal : choisit le regroupement selon
    `config.mode_groupement` ("segments" = phrases naturelles whisper,
    nécessite `segments` ; "groupes_mots" = paquets de N mots, nécessite
    `words`)."""
    if config.mode_groupement == "segments":
        if segments is None:
            raise ValueError("mode_groupement='segments' nécessite des segments (transcription whisper)")
        groups = segments
    else:
        if words is None:
            raise ValueError("mode_groupement='groupes_mots' nécessite des mots horodatés")
        groups = group_words(words, config.mots_par_groupe)
    return build_ass_from_groups(groups, config, video_cfg)


def write_ass(content_or_path: str, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content_or_path, encoding="utf-8")
    return output_path


def burn_subtitles(
    video_path: str | Path,
    ass_path: str | Path,
    output_path: str | Path,
    video_cfg: VideoConfig,
    fonts_dir: Optional[str | Path] = None,
) -> Path:
    """Incruste (burn-in) le fichier .ass dans la vidéo via le filtre libass."""
    ff.check_ffmpeg_available()
    video_path, ass_path, output_path = Path(video_path), Path(ass_path), Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ass_escaped = str(ass_path).replace("\\", "/").replace(":", r"\:")
    vf = f"ass={ass_escaped}"
    if fonts_dir is not None:
        fonts_escaped = str(fonts_dir).replace("\\", "/").replace(":", r"\:")
        vf += f":fontsdir={fonts_escaped}"

    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", vf,
        "-c:v", video_cfg.codec_video, "-crf", str(video_cfg.crf), "-preset", video_cfg.preset,
        "-c:a", "copy",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path
