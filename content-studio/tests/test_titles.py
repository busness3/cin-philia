from content_studio import ffmpeg_utils as ff
from content_studio.models import TitresStyle, VideoConfig
from content_studio.titles import apply_title_overlay, render_title_card

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=480, hauteur=854, fps=24)


def test_render_title_card_carton_plein(tmp_path):
    style = TitresStyle(animation_entree="slide_up", animation_sortie="fade")
    out = render_title_card("Test carton", style, VIDEO_CFG, 1.0, tmp_path / "card.mp4", work_dir=tmp_path)
    info = ff.probe(out)
    assert info.width == VIDEO_CFG.largeur
    assert info.height == VIDEO_CFG.hauteur
    assert info.has_audio is True
    assert abs(info.duration - 1.0) < 0.3


def test_render_title_card_zoom_animation(tmp_path):
    style = TitresStyle(animation_entree="zoom", animation_sortie="none")
    out = render_title_card("Zoom", style, VIDEO_CFG, 1.0, tmp_path / "zoom.mp4", work_dir=tmp_path)
    info = ff.probe(out)
    assert info.width == VIDEO_CFG.largeur


def test_render_title_card_apostrophe_text(tmp_path):
    style = TitresStyle()
    out = render_title_card(
        "j'ai testé: ça marche à 100%", style, VIDEO_CFG, 1.0, tmp_path / "apostrophe.mp4", work_dir=tmp_path
    )
    assert out.exists()


def test_apply_title_overlay_on_existing_clip(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=2.0)
    style = TitresStyle()
    out = apply_title_overlay(
        src, tmp_path / "with_title.mp4", "Accroche", style, VIDEO_CFG,
        start_s=0.0, duration_s=1.0, work_dir=tmp_path,
    )
    info = ff.probe(out)
    assert abs(info.duration - 2.0) < 0.3
