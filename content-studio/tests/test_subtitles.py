from content_studio import ffmpeg_utils as ff
from content_studio.models import SousTitresConfig, VideoConfig
from content_studio.subtitles import build_ass, build_ass_from_groups, burn_subtitles, hex_to_ass_color, write_ass
from content_studio.transcribe import Word, WordGroup

from .helpers import make_synthetic_clip

VIDEO_CFG = VideoConfig(largeur=540, hauteur=960, fps=24)


def test_hex_to_ass_color():
    assert hex_to_ass_color("#4A3328") == "&H0028334A&"
    assert hex_to_ass_color("#F5EFE6") == "&H00E6EFF5&"


def _sample_segments():
    return [
        WordGroup(words=[], start=0.0, end=1.0, texte_brut="Première phrase"),
        WordGroup(words=[], start=1.2, end=2.2, texte_brut="Deuxième phrase, plus longue"),
    ]


def test_build_ass_from_groups_contains_style_and_events():
    cfg = SousTitresConfig()
    ass = build_ass_from_groups(_sample_segments(), cfg, VIDEO_CFG)
    assert "[V4+ Styles]" in ass
    assert "BorderStyle=3" not in ass  # c'est un champ positionnel, pas nommé, dans le Format ASS
    assert "Première phrase" in ass
    assert "Deuxième phrase, plus longue" in ass
    assert ass.count("Dialogue:") == 2


def test_build_ass_segments_mode():
    cfg = SousTitresConfig(mode_groupement="segments")
    ass = build_ass(cfg, VIDEO_CFG, segments=_sample_segments())
    assert ass.count("Dialogue:") == 2


def test_build_ass_segments_mode_missing_segments_raises():
    import pytest

    cfg = SousTitresConfig(mode_groupement="segments")
    with pytest.raises(ValueError):
        build_ass(cfg, VIDEO_CFG, words=[Word("a", 0.0, 0.5)])


def test_build_ass_groupes_mots_mode():
    cfg = SousTitresConfig(mode_groupement="groupes_mots", mots_par_groupe=2)
    words = [Word(f"mot{i}", i * 0.5, i * 0.5 + 0.4) for i in range(4)]
    ass = build_ass(cfg, VIDEO_CFG, words=words)
    assert ass.count("Dialogue:") == 2


def test_backdrop_style_uses_border_style_3():
    cfg = SousTitresConfig()
    ass = build_ass_from_groups(_sample_segments(), cfg, VIDEO_CFG)
    style_line = next(line for line in ass.splitlines() if line.startswith("Style:"))
    fields = style_line[len("Style:"):].split(",")
    # Format: ...,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
    border_style_idx = 15  # cf. l'ordre déclaré dans le header [V4+ Styles]
    assert fields[border_style_idx] == "3"


def test_burn_subtitles_end_to_end(tmp_path):
    src = make_synthetic_clip(tmp_path / "src.mp4", width=960, height=540, duration=2.0)
    cfg = SousTitresConfig()
    ass_content = build_ass_from_groups(_sample_segments(), cfg, VIDEO_CFG)
    ass_path = write_ass(ass_content, tmp_path / "subs.ass")
    assert ass_path.exists()

    out = burn_subtitles(src, ass_path, tmp_path / "out.mp4", VIDEO_CFG)
    info = ff.probe(out)
    assert info.duration > 0
    assert out.exists()
