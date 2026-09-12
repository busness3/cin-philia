from content_studio import ffmpeg_utils as ff
from content_studio.models import CadreOverlay, VideoConfig, Watermark, WatermarkSerie
from content_studio.overlays import (
    apply_cadre,
    apply_image_watermark,
    apply_text_overlays,
    apply_text_watermark,
    position_expr,
)

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=480, hauteur=854, fps=24)


def test_position_expr_all_positions_are_valid_exprs():
    for pos in [
        "haut_gauche", "haut_centre", "haut_droite",
        "centre",
        "bas_gauche", "bas_centre", "bas_droite",
    ]:
        x, y = position_expr(pos, VIDEO_CFG)
        assert isinstance(x, str) and isinstance(y, str)


def test_position_expr_invalid_raises():
    import pytest
    with pytest.raises(ValueError):
        position_expr("nawak", VIDEO_CFG)


def test_apply_text_overlays_end_to_end(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=2.0)
    from content_studio.models import EpisodeConfig, OverlayTexte

    overlays = [
        OverlayTexte(texte="⚠️ spoiler: j'annonce, 100% sûr", debut_s=0.2, fin_s=1.0, position="haut_centre"),
        OverlayTexte(texte="fin", debut_s=1.0, fin_s=1.8, position="bas_gauche"),
    ]
    out = apply_text_overlays(
        src, tmp_path / "out.mp4", overlays, VIDEO_CFG,
        police="DejaVuSans-Bold", taille_px=40, couleur_texte="#FFFFFF", work_dir=tmp_path,
    )
    info = ff.probe(out)
    assert abs(info.duration - 2.0) < 0.3


def test_apply_text_overlays_empty_list_copies(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=1.0)
    out = apply_text_overlays(src, tmp_path / "out.mp4", [], VIDEO_CFG, police="x", taille_px=10, couleur_texte="#FFF")
    assert out.exists()


def test_apply_cadre(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=1.0)
    cadre = CadreOverlay(actif=True, couleur="#FF3B5C", epaisseur_px=12)
    out = apply_cadre(src, tmp_path / "out.mp4", cadre, VIDEO_CFG)
    info = ff.probe(out)
    assert info.width == VIDEO_CFG.largeur


def test_apply_text_watermark(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=1.0)
    wm = WatermarkSerie(actif=True, texte="DIAGNOSTIC SÉRIE", position="haut_gauche")
    out = apply_text_watermark(src, tmp_path / "out.mp4", wm, VIDEO_CFG, police="DejaVuSans-Bold", work_dir=tmp_path)
    assert out.exists()


def test_apply_image_watermark(tmp_path):
    # génère une petite image PNG de logo factice via ffmpeg
    logo = tmp_path / "logo.png"
    ff.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=red:size=100x100:duration=1",
        "-frames:v", "1", "-update", "1", str(logo),
    ])
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=1.0)
    wm = Watermark(actif=True, image=str(logo), position="haut_droite", opacite=0.8)
    out = apply_image_watermark(src, tmp_path / "out.mp4", wm, VIDEO_CFG)
    info = ff.probe(out)
    assert info.width == VIDEO_CFG.largeur
