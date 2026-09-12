"""Utilitaires de test : génère des rushs synthétiques via ffmpeg (lavfi),
pour ne pas dépendre de vrais fichiers vidéo dans les tests."""
from __future__ import annotations

from pathlib import Path

from content_studio import ffmpeg_utils as ff


def make_synthetic_clip(
    path: str | Path,
    width: int = 1920,
    height: int = 1080,
    duration: float = 2.0,
    fps: int = 30,
    with_audio: bool = True,
) -> Path:
    """Génère un petit clip de test (mire animée + éventuellement un bip)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"testsrc2=size={width}x{height}:rate={fps}:duration={duration}",
    ]
    if with_audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}"]
        cmd += ["-c:a", "aac", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)]
    ff.run(cmd)
    return path


def make_synthetic_audio(
    path: str | Path,
    duration: float = 1.0,
    frequency: int = 440,
) -> Path:
    """Génère un fichier audio de test (tonalité pure) pour musique/SFX factices."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={frequency}:duration={duration}",
        "-c:a", "libmp3lame",
        str(path),
    ]
    ff.run(cmd)
    return path
