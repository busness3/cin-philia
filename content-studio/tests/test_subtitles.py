from content_studio import ffmpeg_utils as ff
from content_studio.models import SousTitresStyle, VideoConfig
from content_studio.subtitles import build_ass, burn_subtitles, hex_to_ass_color, write_ass
from content_studio.transcribe import Word

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=540, hauteur=960, fps=24)


def test_hex_to_ass_color():
    assert hex_to_ass_color("#FF3B5C") == "&H005C3BFF&"
    assert hex_to_ass_color("#FFFFFF") == "&H00FFFFFF&"
    assert hex_to_ass_color("#000000", alpha_hex="80") == "&H80000000&"


def _sample_words():
    return [
        Word("Bonjour", 0.0, 0.4),
        Word("à", 0.4, 0.5),
        Word("toutes", 0.5, 0.9),
        Word("et", 1.0, 1.1),
        Word("tous", 1.1, 1.5),
    ]


def test_build_ass_contains_style_and_events():
    style = SousTitresStyle(mots_par_groupe=3, couleur_mot_actif=None)
    ass = build_ass(_sample_words(), style, VIDEO_CFG)
    assert "[V4+ Styles]" in ass
    assert "[Events]" in ass
    assert "BONJOUR" in ass  # majuscules=True par défaut
    assert ass.count("Dialogue:") == 2  # 5 mots / groupes de 3 -> 2 groupes


def test_build_ass_word_highlight_mode():
    style = SousTitresStyle(mots_par_groupe=3, couleur_mot_actif="#FF3B5C")
    ass = build_ass(_sample_words(), style, VIDEO_CFG)
    # un événement par mot quand le surlignage est actif
    assert ass.count("Dialogue:") == len(_sample_words())
    assert "&H005C3BFF&" in ass  # couleur du mot actif présente


def test_build_ass_lowercase_when_disabled():
    style = SousTitresStyle(mots_par_groupe=3, majuscules=False)
    ass = build_ass(_sample_words(), style, VIDEO_CFG)
    assert "Bonjour" in ass
    assert "BONJOUR" not in ass


def test_burn_subtitles_end_to_end(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=960, height=540, duration=2.0)
    style = SousTitresStyle(mots_par_groupe=2, couleur_mot_actif="#FF3B5C")
    ass_path = write_ass(_sample_words(), style, VIDEO_CFG, tmp_path / "subs.ass")
    assert ass_path.exists()

    out = burn_subtitles(src, ass_path, tmp_path / "out.mp4", VIDEO_CFG)
    info = ff.probe(out)
    assert info.duration > 0
    assert out.exists()
