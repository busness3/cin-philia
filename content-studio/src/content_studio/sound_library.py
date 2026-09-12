"""Bibliothèque de sons (musiques + SFX) fournie par Cléa.

Structure attendue sous `sounds/` :
    sounds/
      music/...           fichiers audio musique
      sfx/...             fichiers audio SFX
      index.yaml          associe des clés lisibles (mood, id sfx) aux fichiers

Exemple d'`index.yaml` :

    musique:
      energique:
        - music/energique_01.mp3
        - music/energique_02.mp3
      neutre:
        - music/neutre_01.mp3
    sfx:
      whoosh_court: sfx/whoosh_court.mp3
      pop: sfx/pop.mp3

Un "mood" peut lister plusieurs pistes : une est piochée au hasard, pour
varier les vidéos d'une même série.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

import yaml

from .config import SOUNDS_DIR


class SoundLibraryError(Exception):
    pass


def load_index(sounds_dir: Optional[Path] = None) -> dict:
    sounds_dir = Path(sounds_dir) if sounds_dir else SOUNDS_DIR
    index_path = sounds_dir / "index.yaml"
    if not index_path.exists():
        return {"musique": {}, "sfx": {}}
    with index_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("musique", {})
    data.setdefault("sfx", {})
    return data


def pick_music(
    mood: str,
    sounds_dir: Optional[Path] = None,
    rng: Optional[random.Random] = None,
) -> Path:
    sounds_dir = Path(sounds_dir) if sounds_dir else SOUNDS_DIR
    index = load_index(sounds_dir)
    options = index["musique"].get(mood)
    if not options:
        raise SoundLibraryError(
            f"aucune musique pour le mood {mood!r} dans {sounds_dir / 'index.yaml'} "
            "(ajoute une entrée sous `musique:` de l'index)"
        )
    if isinstance(options, str):
        options = [options]
    chosen = (rng or random).choice(options)
    path = sounds_dir / chosen
    if not path.exists():
        raise SoundLibraryError(f"fichier musique introuvable : {path}")
    return path


def get_sfx(sfx_id: str, sounds_dir: Optional[Path] = None) -> Path:
    sounds_dir = Path(sounds_dir) if sounds_dir else SOUNDS_DIR
    index = load_index(sounds_dir)
    rel = index["sfx"].get(sfx_id)
    if not rel:
        raise SoundLibraryError(
            f"sfx {sfx_id!r} introuvable dans {sounds_dir / 'index.yaml'} "
            "(ajoute une entrée sous `sfx:` de l'index)"
        )
    path = sounds_dir / rel
    if not path.exists():
        raise SoundLibraryError(f"fichier sfx introuvable : {path}")
    return path
