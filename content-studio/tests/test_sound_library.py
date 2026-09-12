import random

import pytest

from content_studio.sound_library import SoundLibraryError, get_sfx, load_index, pick_music


def _make_library(tmp_path):
    (tmp_path / "music").mkdir()
    (tmp_path / "sfx").mkdir()
    (tmp_path / "music" / "energique_01.mp3").write_bytes(b"fake")
    (tmp_path / "music" / "energique_02.mp3").write_bytes(b"fake")
    (tmp_path / "sfx" / "whoosh.mp3").write_bytes(b"fake")
    (tmp_path / "index.yaml").write_text(
        "musique:\n"
        "  energique:\n"
        "    - music/energique_01.mp3\n"
        "    - music/energique_02.mp3\n"
        "sfx:\n"
        "  whoosh_court: sfx/whoosh.mp3\n",
        encoding="utf-8",
    )
    return tmp_path


def test_load_index_missing_file_returns_empty(tmp_path):
    index = load_index(tmp_path)
    assert index == {"musique": {}, "sfx": {}}


def test_pick_music_picks_from_list(tmp_path):
    lib = _make_library(tmp_path)
    rng = random.Random(42)
    path = pick_music("energique", lib, rng=rng)
    assert path.name in ("energique_01.mp3", "energique_02.mp3")
    assert path.exists()


def test_pick_music_unknown_mood_raises(tmp_path):
    lib = _make_library(tmp_path)
    with pytest.raises(SoundLibraryError):
        pick_music("mood_inexistant", lib)


def test_get_sfx(tmp_path):
    lib = _make_library(tmp_path)
    path = get_sfx("whoosh_court", lib)
    assert path.name == "whoosh.mp3"


def test_get_sfx_unknown_raises(tmp_path):
    lib = _make_library(tmp_path)
    with pytest.raises(SoundLibraryError):
        get_sfx("inconnu", lib)
