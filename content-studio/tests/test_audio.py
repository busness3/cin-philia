from content_studio import ffmpeg_utils as ff
from content_studio.audio import mix_audio
from content_studio.models import SfxCue, VideoConfig

from .helpers import make_synthetic_audio, make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=480, hauteur=854, fps=24)


def test_mix_audio_voice_only(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=2.0)
    out = mix_audio(
        src, tmp_path / "out.mp4", VIDEO_CFG, duration_s=2.0,
        music_path=None, music_volume_db=-18, sfx_cues=[], sfx_paths={},
        sfx_default_volume_db=-6, loudness_lufs=-14.0,
    )
    info = ff.probe(out)
    assert info.has_audio
    assert abs(info.duration - 2.0) < 0.3


def test_mix_audio_with_music_and_ducking(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=3.0)
    music = make_synthetic_audio(tmp_path / "music.mp3", duration=1.0, frequency=220)  # plus courte que la vidéo -> doit boucler
    out = mix_audio(
        src, tmp_path / "out.mp4", VIDEO_CFG, duration_s=3.0,
        music_path=music, music_volume_db=-20, sfx_cues=[], sfx_paths={},
        sfx_default_volume_db=-6, loudness_lufs=-14.0, apply_ducking=True,
    )
    info = ff.probe(out)
    assert info.has_audio
    assert abs(info.duration - 3.0) < 0.3


def test_mix_audio_with_sfx_cues(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=2.0)
    sfx = make_synthetic_audio(tmp_path / "sfx.mp3", duration=0.3, frequency=880)
    cues = [SfxCue(id="whoosh", au_temps_s=0.5), SfxCue(id="whoosh", au_temps_s=1.2, volume_db=-3)]
    out = mix_audio(
        src, tmp_path / "out.mp4", VIDEO_CFG, duration_s=2.0,
        music_path=None, music_volume_db=-18, sfx_cues=cues,
        sfx_paths={"whoosh": sfx, "whoosh_bis": sfx},
        sfx_default_volume_db=-6, loudness_lufs=-14.0,
    )
    info = ff.probe(out)
    assert info.has_audio
    assert abs(info.duration - 2.0) < 0.3


def test_mix_audio_music_and_sfx_together(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=2.5)
    music = make_synthetic_audio(tmp_path / "music.mp3", duration=4.0, frequency=220)
    sfx = make_synthetic_audio(tmp_path / "sfx.mp3", duration=0.2, frequency=1000)
    cues = [SfxCue(id="pop", au_temps_s=1.0)]
    out = mix_audio(
        src, tmp_path / "out.mp4", VIDEO_CFG, duration_s=2.5,
        music_path=music, music_volume_db=-18, sfx_cues=cues,
        sfx_paths={"pop": sfx},
        sfx_default_volume_db=-6, loudness_lufs=-14.0,
    )
    info = ff.probe(out)
    assert info.has_audio
    assert abs(info.duration - 2.5) < 0.3
