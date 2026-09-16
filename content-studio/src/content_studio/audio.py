"""Brique 5 : mixage musique + SFX (bibliothèque) avec la voix des rushs.

- La musique est bouclée/coupée à la durée de la vidéo, jouée en dessous du
  volume réglé par la série, avec ducking (baisse automatique le temps que la
  voix parle) via `sidechaincompress` piloté par la piste voix.
- Chaque SFX est décalé (adelay) à son instant de déclenchement (`au_temps_s`).
- Le mix final passe par un limiteur puis un `loudnorm` calé sur la loudness
  cible définie dans `configs/global.yaml` (cohérence entre épisodes/séries).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import ffmpeg_utils as ff
from .models import SfxCue, VideoConfig

_DUCK_THRESHOLD_LINEAR = 10 ** (-24 / 20)  # ~ -24 dBFS : seuil de déclenchement du ducking


def build_audio_filter(
    duration_s: float,
    has_music: bool,
    music_volume_db: float,
    sfx_cues: list[SfxCue],
    sfx_default_volume_db: float,
    loudness_lufs: float,
    apply_ducking: bool = True,
    music_delay_s: float = 0.0,
) -> str:
    """Construit le filter_complex audio. Entrées attendues, dans l'ordre :
    0 = voix (piste audio de la vidéo normalisée), 1 = musique (si présente),
    puis un input par SFX (dans l'ordre de `sfx_cues`)."""
    do_duck = has_music and apply_ducking
    parts: list[str] = []
    labels: list[str] = []

    if do_duck:
        parts.append("[0:a]asplit=2[voice_dry][voice_sc]")
    else:
        parts.append("[0:a]anull[voice_dry]")
    labels.append("voice_dry")

    if has_music:
        delay_clause = ""
        if music_delay_s > 0:
            delay_ms = round(music_delay_s * 1000)
            delay_clause = f",adelay={delay_ms}|{delay_ms}"
        parts.append(
            f"[1:a]volume={music_volume_db}dB,aloop=loop=-1:size=2e9,"
            f"atrim=0:{duration_s},asetpts=PTS-STARTPTS{delay_clause}[music_a]"
        )
        if do_duck:
            parts.append(
                f"[music_a][voice_sc]sidechaincompress="
                f"threshold={_DUCK_THRESHOLD_LINEAR:.4f}:ratio=8:attack=5:release=300[music_ducked]"
            )
            labels.append("music_ducked")
        else:
            labels.append("music_a")

    sfx_base_idx = 2 if has_music else 1
    for i, cue in enumerate(sfx_cues):
        vol = cue.volume_db if cue.volume_db is not None else sfx_default_volume_db
        delay_ms = max(int(round(cue.au_temps_s * 1000)), 0)
        label = f"sfx{i}"
        parts.append(f"[{sfx_base_idx + i}:a]volume={vol}dB,adelay={delay_ms}|{delay_ms}[{label}]")
        labels.append(label)

    mix_inputs = "".join(f"[{l}]" for l in labels)
    parts.append(f"{mix_inputs}amix=inputs={len(labels)}:duration=first:dropout_transition=0:normalize=0[premix]")
    parts.append("[premix]alimiter=limit=0.95[limited]")
    parts.append(f"[limited]loudnorm=I={loudness_lufs}:TP=-1.5:LRA=11[aout]")

    return ";".join(parts)


def mix_audio(
    video_path: str | Path,
    output_path: str | Path,
    video_cfg: VideoConfig,
    duration_s: float,
    music_path: Optional[Path],
    music_volume_db: float,
    sfx_cues: list[SfxCue],
    sfx_paths: dict[str, Path],
    sfx_default_volume_db: float,
    loudness_lufs: float,
    apply_ducking: bool = True,
    music_delay_s: float = 0.0,
) -> Path:
    ff.check_ffmpeg_available()
    video_path, output_path = Path(video_path), Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-i", str(video_path)]
    if music_path is not None:
        cmd += ["-i", str(music_path)]
    for cue in sfx_cues:
        cmd += ["-i", str(sfx_paths[cue.id])]

    filter_str = build_audio_filter(
        duration_s=duration_s,
        has_music=music_path is not None,
        music_volume_db=music_volume_db,
        sfx_cues=sfx_cues,
        sfx_default_volume_db=sfx_default_volume_db,
        loudness_lufs=loudness_lufs,
        apply_ducking=apply_ducking,
        music_delay_s=music_delay_s,
    )

    cmd += [
        "-filter_complex", filter_str,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", video_cfg.codec_audio, "-b:a", video_cfg.bitrate_audio,
        "-shortest",
        str(output_path),
    ]
    ff.run(cmd)
    return output_path
