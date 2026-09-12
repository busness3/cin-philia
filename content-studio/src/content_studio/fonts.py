"""Résolution des polices pour drawtext (fontfile=chemin absolu).

Cherche `{fonts_dir}/{nom}.{ttf,otf,ttc}`. Si la police n'est pas encore
fournie par Cléa, retombe sur une police système de secours pour ne pas
bloquer les tests/rendus — un avertissement est renvoyé dans ce cas.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import ASSETS_DIR

_FALLBACK_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


class FontError(Exception):
    pass


def resolve_font_path(name: str, fonts_dir: Optional[Path] = None) -> Path:
    fonts_dir = Path(fonts_dir) if fonts_dir else (ASSETS_DIR / "fonts")
    for ext in (".ttf", ".otf", ".ttc"):
        candidate = fonts_dir / f"{name}{ext}"
        if candidate.exists():
            return candidate

    for fb in _FALLBACK_CANDIDATES:
        if fb.exists():
            return fb

    raise FontError(
        f"police {name!r} introuvable dans {fonts_dir} et aucune police de repli "
        "disponible sur le système. Dépose le fichier .ttf/.otf correspondant "
        f"dans assets/fonts/{name}.ttf"
    )
