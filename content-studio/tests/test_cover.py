from content_studio import ffmpeg_utils as ff
from content_studio.cover import generate_cover
from content_studio.models import GabaritCouverture, VideoConfig

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=480, hauteur=854, fps=24)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def test_generate_cover_produces_png(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=1.0)
    gabarit = GabaritCouverture()
    out = generate_cover(
        src, tmp_path / "cover.png", gabarit, "#D89A1E", FONT, 60,
        "Test Resto", VIDEO_CFG, temps_capture_s=0.2, work_dir=tmp_path,
    )
    assert out.exists()
    assert out.suffix == ".png"
    info = ff.ffprobe_json(out)
    stream = info["streams"][0]
    assert int(stream["width"]) == VIDEO_CFG.largeur
    assert int(stream["height"]) == VIDEO_CFG.hauteur
