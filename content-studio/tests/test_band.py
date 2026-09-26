from content_studio import ffmpeg_utils as ff
from content_studio.band import apply_animated_band_to_video, apply_band_to_video, band_filters, split_title_lines
from content_studio.models import GabaritCouverture, VideoConfig

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=480, hauteur=854, fps=24)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def test_split_title_lines_manual_newline():
    l1, l2 = split_title_lines("Diagnostic express\nla suite")
    assert l1 == "Diagnostic express"
    assert l2 == "la suite"


def test_split_title_lines_auto_split():
    l1, l2 = split_title_lines("Un titre assez long")
    assert l1 == "Un titre"
    assert l2 == "assez long"


def test_split_title_lines_single_word():
    l1, l2 = split_title_lines("Verdict")
    assert l1 == "Verdict"
    assert l2 == ""


def test_band_filters_count_with_two_lines(tmp_path):
    gabarit = GabaritCouverture()
    filters = band_filters(gabarit, "#D42A2A", FONT, 96, "Titre court ici", tmp_path, "test")
    # 2 drawbox (bandeau + bloc accent) + 2 drawtext (2 lignes)
    assert len(filters) == 4
    assert filters[0].startswith("drawbox")
    assert filters[1].startswith("drawbox")
    assert filters[2].startswith("drawtext")
    assert filters[3].startswith("drawtext")


def test_band_filters_count_with_one_line(tmp_path):
    gabarit = GabaritCouverture()
    filters = band_filters(gabarit, "#D42A2A", FONT, 96, "Verdict", tmp_path, "test")
    assert len(filters) == 3


def test_apply_band_to_video_timing(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=3.0)
    gabarit = GabaritCouverture(
        bandeau={"x": 0, "y": 500, "largeur": 480, "hauteur": 150, "couleur_fond": "#F5EFE6"},
        bloc_accent={"x": 20, "y": 520, "largeur": 8, "hauteur": 50},
        titre={"x": 40, "baseline_ligne1_y": 560, "baseline_ligne2_y": 600, "largeur_max_px": 400,
               "max_lignes": 2, "max_mots": 4, "couleur_texte": "#4A3328"},
    )
    out = apply_band_to_video(
        src, tmp_path / "out.mp4", gabarit, "#D42A2A", FONT, 40, "Titre test",
        VIDEO_CFG, start_s=0.3, duration_s=1.0, work_dir=tmp_path,
    )
    info = ff.probe(out)
    assert abs(info.duration - 3.0) < 0.3
    assert out.exists()


def test_apply_animated_band_to_video_timing(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=480, height=854, duration=3.0, with_audio=True)
    gabarit = GabaritCouverture(
        bandeau={"x": 0, "y": 500, "largeur": 480, "hauteur": 150, "couleur_fond": "#F5EFE6"},
    )
    # clip d'habillage : bloc rouge uni, taille exacte du bandeau (480x150)
    clip_anime = tmp_path / "titre.mp4"
    ff.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=red:s=480x150:d=1:r=24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip_anime),
    ])

    out = apply_animated_band_to_video(
        src, tmp_path / "out.mp4", gabarit, VIDEO_CFG, clip_anime,
        start_s=0.5, duration_s=1.0,
    )
    info = ff.probe(out)
    assert out.exists()
    assert info.has_audio
    assert abs(info.duration - 3.0) < 0.3

    # avant/après la fenêtre : pas de rouge dans la zone du bandeau ;
    # pendant : rouge.
    def _extract_pixel(t: float) -> str:
        frame = tmp_path / f"frame_{t}.png"
        ff.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(out), "-frames:v", "1", str(frame)])
        return frame.read_bytes()

    before = _extract_pixel(0.1)
    during = _extract_pixel(0.9)
    after = _extract_pixel(2.5)
    assert before != during
    assert after != during
