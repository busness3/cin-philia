"""Construction de filtres ffmpeg `drawtext` robuste au texte libre.

Le texte est toujours écrit dans un fichier temporaire et référencé via
`textfile=` plutôt que passé inline via `text=`. Testé empiriquement : passer
du texte contenant apostrophes/deux-points/virgules directement dans
`text='...'` casse le parseur de filtres ffmpeg de façon silencieuse (le
texte suivant est absorbé, la couleur/police par défaut s'applique — donc
aucune erreur, juste un rendu invisible). Passer par un fichier élimine tous
ces pièges d'échappement ; seul le caractère `%` doit encore être échappé
(`\\%`) car `drawtext` l'interprète pour l'expansion de variables même en
lisant un fichier.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


def escape_textfile_content(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%")


def escape_filter_path(path: str | Path) -> str:
    """Échappe un chemin pour l'utiliser comme valeur d'option dans un filtre
    ffmpeg (les ':' séparent les options, doivent donc être échappés)."""
    return str(path).replace("\\", "\\\\").replace(":", "\\:")


def write_textfile(text: str, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(escape_textfile_content(text), encoding="utf-8")
    return path


def hex_to_ffmpeg_color(hex_color: str) -> str:
    """#RRGGBB -> 0xRRGGBB (format couleur accepté par les filtres ffmpeg)."""
    return "0x" + hex_color.lstrip("#")


def drawtext_filter(
    textfile_path: str | Path,
    fontfile_path: str | Path,
    fontsize: int,
    fontcolor: str,
    x: str,
    y: str,
    alpha: Optional[str] = None,
    borderw: int = 0,
    bordercolor: Optional[str] = None,
    enable: Optional[str] = None,
) -> str:
    """Construit la chaîne `drawtext=...` (sans le `[label]` d'entrée/sortie)."""
    parts = [
        f"fontfile={escape_filter_path(fontfile_path)}",
        f"textfile={escape_filter_path(textfile_path)}",
        f"fontsize={fontsize}",
        f"fontcolor={fontcolor}",
        f"x={x}",
        f"y={y}",
    ]
    if alpha is not None:
        parts.append(f"alpha={alpha}")
    if borderw:
        parts.append(f"borderw={borderw}")
    if bordercolor:
        parts.append(f"bordercolor={bordercolor}")
    if enable is not None:
        parts.append(f"enable={enable}")
    return "drawtext=" + ":".join(parts)
