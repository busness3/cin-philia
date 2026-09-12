"""Tests de la brique normalisation (rushs -> format proxy standard)."""
from pathlib import Path

import pytest

from content_studio import ffmpeg_utils as ff
from content_studio.models import VideoConfig
from content_studio.normalize import normalize_clip

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=540, hauteur=960, fps=24)  # petit format pour des tests rapides


def test_normalize_landscape_cover(tmp_path):
    src = make_synthetic_clip(tmp_path / "src_paysage.mp4", width=1280, height=720, duration=1.0)
    out = normalize_clip(src, tmp_path / "out.mp4", VIDEO_CFG, mode="cover")

    info = ff.probe(out)
    assert info.width == VIDEO_CFG.largeur
    assert info.height == VIDEO_CFG.hauteur
    assert info.has_audio is True
    assert abs(info.duration - 1.0) < 0.2


def test_normalize_portrait_contain_blur(tmp_path):
    src = make_synthetic_clip(tmp_path / "src_portrait.mp4", width=720, height=1280, duration=1.0)
    out = normalize_clip(src, tmp_path / "out2.mp4", VIDEO_CFG, mode="contain_blur")

    info = ff.probe(out)
    assert info.width == VIDEO_CFG.largeur
    assert info.height == VIDEO_CFG.hauteur


def test_normalize_adds_silent_audio_when_missing(tmp_path):
    src = make_synthetic_clip(tmp_path / "src_muet.mp4", width=640, height=360, duration=1.0, with_audio=False)
    src_info = ff.probe(src)
    assert src_info.has_audio is False

    out = normalize_clip(src, tmp_path / "out3.mp4", VIDEO_CFG, mode="cover")
    out_info = ff.probe(out)
    assert out_info.has_audio is True


def test_normalize_trims_start_end(tmp_path):
    src = make_synthetic_clip(tmp_path / "src_long.mp4", width=640, height=360, duration=4.0)
    out = normalize_clip(src, tmp_path / "out4.mp4", VIDEO_CFG, mode="cover", start=1.0, end=2.5)
    info = ff.probe(out)
    assert abs(info.duration - 1.5) < 0.2


def test_normalize_missing_input_raises(tmp_path):
    with pytest.raises(ff.FFmpegError):
        normalize_clip(tmp_path / "nope.mp4", tmp_path / "out.mp4", VIDEO_CFG)
