import pytest

from content_studio import ffmpeg_utils as ff
from content_studio.models import VideoConfig
from content_studio.normalize import normalize_clip
from content_studio.transitions import concat_with_transitions

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=480, hauteur=854, fps=24)


def _normalized_clips(tmp_path, n=3, duration=1.5):
    clips = []
    for i in range(n):
        raw = make_synthetic_clip(tmp_path / f"raw{i}.mp4", width=640, height=360, duration=duration)
        norm = normalize_clip(raw, tmp_path / f"norm{i}.mp4", VIDEO_CFG, mode="cover")
        clips.append(norm)
    return clips


def test_concat_single_clip(tmp_path):
    clips = _normalized_clips(tmp_path, n=1)
    out = concat_with_transitions(clips, [], 0.3, tmp_path / "out.mp4", VIDEO_CFG)
    info = ff.probe(out)
    assert abs(info.duration - 1.5) < 0.3


def test_concat_cut_only(tmp_path):
    clips = _normalized_clips(tmp_path, n=3, duration=1.0)
    out = concat_with_transitions(clips, ["cut", "cut"], 0.3, tmp_path / "out.mp4", VIDEO_CFG)
    info = ff.probe(out)
    # 3 x 1.0s bout à bout, sans recouvrement
    assert abs(info.duration - 3.0) < 0.3
    assert info.width == VIDEO_CFG.largeur


def test_concat_fade_transition_shortens_total(tmp_path):
    clips = _normalized_clips(tmp_path, n=2, duration=2.0)
    out_cut = concat_with_transitions(clips, ["cut"], 0.4, tmp_path / "cut.mp4", VIDEO_CFG)
    out_fade = concat_with_transitions(clips, ["fade"], 0.4, tmp_path / "fade.mp4", VIDEO_CFG)
    dur_cut = ff.probe(out_cut).duration
    dur_fade = ff.probe(out_fade).duration
    # le fondu recouvre 0.4s -> la durée totale doit être ~0.4s plus courte que le cut
    assert dur_cut - dur_fade == pytest.approx(0.4, abs=0.2)


def test_concat_all_transition_types(tmp_path):
    clips = _normalized_clips(tmp_path, n=4, duration=1.0)
    out = concat_with_transitions(
        clips, ["cut", "fade", "slide"], 0.3, tmp_path / "out.mp4", VIDEO_CFG
    )
    info = ff.probe(out)
    assert info.has_audio
    assert info.width == VIDEO_CFG.largeur


def test_concat_zoom_transition(tmp_path):
    clips = _normalized_clips(tmp_path, n=2, duration=1.0)
    out = concat_with_transitions(clips, ["zoom"], 0.3, tmp_path / "out.mp4", VIDEO_CFG)
    assert out.exists()


def test_concat_wrong_transition_count_raises(tmp_path):
    clips = _normalized_clips(tmp_path, n=3, duration=1.0)
    with pytest.raises(ValueError):
        concat_with_transitions(clips, ["cut"], 0.3, tmp_path / "out.mp4", VIDEO_CFG)


def test_concat_unknown_transition_raises(tmp_path):
    clips = _normalized_clips(tmp_path, n=2, duration=1.0)
    with pytest.raises(ValueError):
        concat_with_transitions(clips, ["n_importe_quoi"], 0.3, tmp_path / "out.mp4", VIDEO_CFG)
