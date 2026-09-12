from types import SimpleNamespace

from content_studio.transcribe import group_words, parse_srt, words_from_whisper_segments


def _fake_segment(words):
    fake_words = [SimpleNamespace(word=w[0], start=w[1], end=w[2]) for w in words]
    return SimpleNamespace(words=fake_words)


def test_words_from_whisper_segments():
    segments = [
        _fake_segment([(" Bonjour", 0.0, 0.4), (" à", 0.4, 0.5), (" toutes", 0.5, 0.9)]),
        _fake_segment([(" et", 1.0, 1.1), (" tous", 1.1, 1.4)]),
    ]
    words = words_from_whisper_segments(segments)
    assert [w.text for w in words] == ["Bonjour", "à", "toutes", "et", "tous"]
    assert words[0].start == 0.0
    assert words[2].end == 0.9


def test_words_from_whisper_segments_skips_empty():
    segments = [_fake_segment([("  ", 0.0, 0.1), (" ok", 0.1, 0.3)])]
    words = words_from_whisper_segments(segments)
    assert [w.text for w in words] == ["ok"]


def test_group_words_basic():
    segments = [_fake_segment([(f" mot{i}", i, i + 0.5) for i in range(7)])]
    words = words_from_whisper_segments(segments)
    groups = group_words(words, mots_par_groupe=3)
    assert len(groups) == 3  # 3 + 3 + 1
    assert groups[0].text == "mot0 mot1 mot2"
    assert groups[-1].text == "mot6"


def test_group_words_no_overlap():
    segments = [_fake_segment([(" a", 0.0, 0.4), (" b", 2.0, 2.4)])]
    words = words_from_whisper_segments(segments)
    groups = group_words(words, mots_par_groupe=1, trailing_pad_s=5.0)
    # le padding généreux du groupe "a" ne doit pas dépasser le début de "b"
    assert groups[0].end <= groups[1].start


def test_parse_srt(tmp_path):
    srt = (
        "1\n00:00:00,000 --> 00:00:02,000\nPremière ligne\n\n"
        "2\n00:00:02,500 --> 00:00:04,000\nDeuxième ligne\nsur deux mots\n"
    )
    path = tmp_path / "test.srt"
    path.write_text(srt, encoding="utf-8")
    groups = parse_srt(path)
    assert len(groups) == 2
    assert groups[0].text == "Première ligne"
    assert groups[0].start == 0.0
    assert groups[0].end == 2.0
    assert groups[1].text == "Deuxième ligne sur deux mots"
