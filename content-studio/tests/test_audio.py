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


def test_mix_audio_music_delay_after_voice(tmp_path):
    # vidéo avec une piste "voix" silencieuse (anullsrc) : tout le volume
    # mesuré dans le mix final vient donc de la musique -> sert à vérifier
    # qu'elle ne démarre bien qu'après music_delay_s.
    src = tmp_path / "src.mp4"
    ff.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc2=size=480x854:rate=24:duration=3",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        str(src),
    ])
    music = make_synthetic_audio(tmp_path / "music.mp3", duration=3.0, frequency=220)
    out = mix_audio(
        src, tmp_path / "out.mp4", VIDEO_CFG, duration_s=3.0,
        music_path=music, music_volume_db=-6, sfx_cues=[], sfx_paths={},
        sfx_default_volume_db=-6, loudness_lufs=-14.0, apply_ducking=False,
        music_delay_s=1.5,
    )
    info = ff.probe(out)
    assert info.has_audio
    # avant 1.5s : pas de musique (silence, la vidéo source est muette) ;
    # après 1.5s : la musique doit être audible.
    ff.run([
        "ffmpeg", "-y", "-i", str(out), "-t", "1.4", "-af", "volumedetect", "-f", "null", "-",
    ])
    proc_before = ff.run([
        "ffmpeg", "-y", "-i", str(out), "-t", "1.4", "-af", "volumedetect", "-f", "null", "-",
    ])
    proc_after = ff.run([
        "ffmpeg", "-y", "-ss", "2.0", "-i", str(out), "-t", "0.8", "-af", "volumedetect", "-f", "null", "-",
    ])

    def _mean_volume(stderr: str) -> float:
        for line in stderr.splitlines():
            if "mean_volume" in line:
                return float(line.split(":")[1].strip().replace(" dB", ""))
        return -999.0

    vol_before = _mean_volume(proc_before.stderr)
    vol_after = _mean_volume(proc_after.stderr)
    # loudnorm relève un peu le plancher du silence, donc l'écart n'est pas
    # infini, mais doit rester net.
    assert vol_before < vol_after - 8
