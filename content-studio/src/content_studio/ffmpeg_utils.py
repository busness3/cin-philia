"""Wrappers bas niveau autour de ffmpeg/ffprobe : exécution, probing média."""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class FFmpegError(Exception):
    pass


def check_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise FFmpegError(
            "ffmpeg/ffprobe introuvables dans le PATH. Installe ffmpeg "
            "(ex: `brew install ffmpeg` sur Mac, `apt install ffmpeg` sur Linux)."
        )


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Exécute une commande (ffmpeg/ffprobe) et capture stdout/stderr."""
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and proc.returncode != 0:
        raise FFmpegError(
            "commande échouée :\n"
            f"  {' '.join(cmd)}\n"
            f"--- stderr (fin) ---\n{proc.stderr[-4000:]}"
        )
    return proc


def ffprobe_json(path: str | Path) -> dict:
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    proc = run(cmd)
    return json.loads(proc.stdout)


def _parse_rate(rate: str) -> float:
    if not rate or rate == "0/0":
        return 0.0
    if "/" in rate:
        num, den = rate.split("/")
        den = float(den)
        return float(num) / den if den else 0.0
    return float(rate)


@dataclass
class MediaInfo:
    width: int
    height: int
    fps: float
    duration: float
    has_audio: bool
    has_video: bool

    @property
    def orientation(self) -> str:
        if self.width > self.height:
            return "paysage"
        if self.width < self.height:
            return "portrait"
        return "carre"


def probe(path: str | Path) -> MediaInfo:
    """Interroge ffprobe et renvoie les infos utiles d'un fichier média."""
    data = ffprobe_json(path)
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if video_stream is None:
        raise FFmpegError(f"aucun flux vidéo trouvé dans {path}")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    fps = _parse_rate(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate") or "0/1")
    duration_raw = data.get("format", {}).get("duration") or video_stream.get("duration")
    duration = float(duration_raw) if duration_raw else 0.0

    return MediaInfo(
        width=width,
        height=height,
        fps=fps,
        duration=duration,
        has_audio=audio_stream is not None,
        has_video=True,
    )
