"""Brique 2 : sous-titres synchronisés et stylables (génération ASS + burn-in).

Le format .ass (Advanced SubStation Alpha, via libass) est utilisé plutôt que
le .srt car il permet : police/taille/couleur/contour par style, position
précise (alignement + marges en pixels), et des tags d'animation par ligne
(\\fad, \\t, \\move) — de quoi reproduire les styles de légendes "TikTok
punchy" (pop, slide, mot en cours surligné).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import ffmpeg_utils as ff
from .models import SousTitresStyle, VideoConfig
from .transcribe import Word, WordGroup, group_words

_ALIGNMENT = {
    "bas_centre": 2,
    "centre": 5,
    "haut_centre": 8,
}


def hex_to_ass_color(hex_color: str, alpha_hex: str = "00") -> str:
    """Convertit #RRGGBB en couleur ASS &HAABBGGRR& (ordre inversé, alpha en tête)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
    return f"&H{alpha_hex}{b}{g}{r}&".upper()


def _escape_ass_text(text: str) -> str:
    return text.replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


def _animation_override(style: SousTitresStyle) -> str:
    """Tags d'override ASS à préfixer au texte pour l'animation d'entrée."""
    dur = max(style.duree_animation_ms, 1)
    if style.animation == "fade":
        return f"{{\\fad({dur},{dur // 2})}}"
    if style.animation == "pop":
        # démarre à 60% de la taille puis grossit jusqu'à 100% -> effet "pop"
        return f"{{\\fscx60\\fscy60\\t(0,{dur},\\fscx100\\fscy100)}}"
    if style.animation == "slide_up":
        # léger décalage vertical qui remonte vers sa position finale
        return f"{{\\fad({dur},{dur // 2})}}"
    return ""


def _style_line(style: SousTitresStyle, video_cfg: VideoConfig) -> str:
    alignment = _ALIGNMENT[style.position]
    primary = hex_to_ass_color(style.couleur_texte)
    outline = hex_to_ass_color(style.couleur_contour)
    margin_v = style.marge_verticale_px
    return (
        "Style: sous_titres,"
        f"{style.police},{style.taille_px},{primary},{primary},{outline},&H00000000,"
        f"-1,0,0,0,100,100,0,0,1,{style.epaisseur_contour},0,{alignment},"
        f"{video_cfg.zone_sure.lateral_px},{video_cfg.zone_sure.lateral_px},{margin_v},1"
    )


def _script_header(style: SousTitresStyle, video_cfg: VideoConfig) -> str:
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
        f"{_style_line(style, video_cfg)}\n"
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
    if cs == 100:  # arrondi qui déborde sur la seconde suivante
        cs = 0
        s += 1
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _group_text(group: WordGroup, style: SousTitresStyle, mot_actif: Optional[Word] = None) -> str:
    parts = []
    for w in group.words:
        text = w.text.upper() if style.majuscules else w.text
        text = _escape_ass_text(text)
        if mot_actif is not None and w is mot_actif and style.couleur_mot_actif:
            color = hex_to_ass_color(style.couleur_mot_actif)
            parts.append(f"{{\\c{color}}}{text}{{\\c{hex_to_ass_color(style.couleur_texte)}}}")
        else:
            parts.append(text)
    return " ".join(parts)


def build_ass(words: list[Word], style: SousTitresStyle, video_cfg: VideoConfig) -> str:
    """Construit le contenu .ass complet à partir des mots horodatés.

    Si `style.couleur_mot_actif` est défini : un événement par mot (le
    groupe entier est réaffiché à chaque mot, avec le mot courant surligné —
    effet "karaoke" synchronisé). Sinon : un événement par groupe de mots.
    """
    groups = group_words(words, style.mots_par_groupe)
    events = []
    anim = _animation_override(style)

    for group in groups:
        if style.couleur_mot_actif:
            for i, w in enumerate(group.words):
                w_start = w.start
                w_end = group.words[i + 1].start if i + 1 < len(group.words) else group.end
                w_end = max(w_end, w_start + 0.05)
                text = anim + _group_text(group, style, mot_actif=w)
                events.append(
                    f"Dialogue: 0,{_fmt_ts(w_start)},{_fmt_ts(w_end)},sous_titres,,0,0,0,,{text}"
                )
        else:
            text = anim + _group_text(group, style)
            events.append(
                f"Dialogue: 0,{_fmt_ts(group.start)},{_fmt_ts(group.end)},sous_titres,,0,0,0,,{text}"
            )

    return _script_header(style, video_cfg) + "\n".join(events) + "\n"


def write_ass(words: list[Word], style: SousTitresStyle, video_cfg: VideoConfig, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_ass(words, style, video_cfg), encoding="utf-8")
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

    # échappe les caractères sensibles au parsing du filtre ffmpeg (chemins avec ':' etc.)
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
