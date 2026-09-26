import content_studio.config as cfgmod
import content_studio.pipeline as pipeline
from content_studio import ffmpeg_utils as ff

from .helpers import make_synthetic_clip

_GLOBAL_YAML = """
identite:
  nom_compte: "@test"
video:
  largeur: 360
  hauteur: 640
  fps: 24
  codec_video: libx264
  crf: 28
  preset: ultrafast
  codec_audio: aac
  bitrate_audio: 128k
audio:
  loudness_cible_lufs: -14.0
"""


def _setup_project(tmp_path, monkeypatch, series_yaml: str = "nom: Test Serie\naccent: \"#AA3300\"\n"):
    configs_dir = tmp_path / "configs"
    series_dir = configs_dir / "series"
    series_dir.mkdir(parents=True)
    (configs_dir / "global.yaml").write_text(_GLOBAL_YAML, encoding="utf-8")
    (series_dir / "test_serie.yaml").write_text(series_yaml, encoding="utf-8")

    monkeypatch.setattr(cfgmod, "CONFIGS_DIR", configs_dir)
    monkeypatch.setattr(cfgmod, "SERIES_DIR", series_dir)
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(pipeline, "SOUNDS_DIR", tmp_path / "sounds")
    monkeypatch.setattr(pipeline, "ASSETS_DIR", tmp_path / "assets")


def test_render_episode_end_to_end_with_opening_band(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=2.0)

    episode_path = tmp_path / "ep.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test\n"
        "sortie: out/test_final.mp4\n"
        "accroche:\n"
        "  texte: \"Salut à toutes\"\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n",
        encoding="utf-8",
    )

    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()
    info = ff.probe(out)
    assert info.has_audio
    assert info.width == 360 and info.height == 640
    # le titre est incrusté sur le plan existant (pas un carton séparé) ->
    # la durée reste celle du rush, pas rush + accroche.
    assert 1.7 < info.duration < 2.3
    # dossier de travail nettoyé
    assert not (tmp_path / "out" / ".tmp_test_final").exists()
    # pas de couverture générée automatiquement (Cléa s'en charge elle-même)
    assert not (tmp_path / "out" / "test_final_couverture.png").exists()


def test_render_episode_no_music_by_default(tmp_path, monkeypatch):
    # série avec un mood par défaut, mais l'épisode ne demande pas de
    # musique -> pas de musique ajoutée (pas de pioche dans la bibliothèque).
    _setup_project(tmp_path, monkeypatch)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=1.5)

    calls = []

    def _fail_if_called(*a, **k):
        calls.append(a)
        raise AssertionError("pick_music ne devrait pas être appelé sans demande explicite")

    monkeypatch.setattr(pipeline, "pick_music", _fail_if_called)

    episode_path = tmp_path / "ep_no_music.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Sans musique\n"
        "sortie: out/no_music.mp4\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n",
        encoding="utf-8",
    )
    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()
    assert calls == []


def test_render_episode_music_when_explicitly_requested(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=1.5)

    sounds_dir = tmp_path / "sounds"
    (sounds_dir / "music").mkdir(parents=True)
    music_file = sounds_dir / "music" / "test.mp3"
    from .helpers import make_synthetic_audio
    make_synthetic_audio(music_file, duration=2.0, frequency=220)
    (sounds_dir / "index.yaml").write_text("musique:\n  energique:\n    - music/test.mp3\n", encoding="utf-8")

    episode_path = tmp_path / "ep_with_music.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Avec musique\n"
        "sortie: out/with_music.mp4\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n"
        "audio:\n"
        "  mood_musique: energique\n",
        encoding="utf-8",
    )
    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()


def test_render_episode_two_sequences_with_transition(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    rush1 = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=1.5)
    rush2 = make_synthetic_clip(tmp_path / "rush2.mp4", width=640, height=360, duration=1.5)

    episode_path = tmp_path / "ep2.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test 2\n"
        "sortie: out/test2_final.mp4\n"
        "sequences:\n"
        f"  - rush: \"{rush1}\"\n"
        "    sous_titres: aucun\n"
        "    transition_sortie: fade\n"
        f"  - rush: \"{rush2}\"\n"
        "    sous_titres: aucun\n",
        encoding="utf-8",
    )

    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()
    info = ff.probe(out)
    assert info.has_audio


def test_render_episode_overlay_and_outro_band(tmp_path, monkeypatch):
    series_yaml = (
        "nom: Test Serie\n"
        "accent: \"#AA3300\"\n"
        "cta_sortie: \"Dites-moi tout\"\n"
    )
    _setup_project(tmp_path, monkeypatch, series_yaml=series_yaml)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=5.0)

    episode_path = tmp_path / "ep3.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test 3\n"
        "sortie: out/test3_final.mp4\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n"
        "    overlay_texte:\n"
        "      - texte: \"alerte\"\n"
        "        debut_s: 0.2\n"
        "        fin_s: 1.0\n"
        "        position: bas_centre\n",
        encoding="utf-8",
    )

    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()
    info = ff.probe(out)
    assert info.has_audio
    assert 4.7 < info.duration < 5.3


def test_render_episode_outro_suppressed_per_episode(tmp_path, monkeypatch):
    # la série a un cta_sortie (donc le bandeau serait actif par défaut),
    # mais CET épisode le désactive explicitement -> pas de plantage, pas de
    # bandeau de sortie pour cette vidéo précise seulement.
    series_yaml = (
        "nom: Test Serie\n"
        "accent: \"#AA3300\"\n"
        "cta_sortie: \"Dites-moi tout\"\n"
    )
    _setup_project(tmp_path, monkeypatch, series_yaml=series_yaml)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=3.0)

    episode_path = tmp_path / "ep6.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test 6\n"
        "sortie: out/test6_final.mp4\n"
        "sortie_activee: false\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n",
        encoding="utf-8",
    )
    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()


def test_render_episode_no_outro_when_cta_absent(tmp_path, monkeypatch):
    # sans cta_sortie défini par la série, pas de bandeau de sortie -> ne
    # doit pas planter, juste être ignoré.
    _setup_project(tmp_path, monkeypatch)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=3.0)

    episode_path = tmp_path / "ep5.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test 5\n"
        "sortie: out/test5_final.mp4\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n",
        encoding="utf-8",
    )
    out = pipeline.render_episode(episode_path, keep_intermediates=False)
    assert out.exists()


def test_render_episode_keep_intermediates(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=1.0)

    episode_path = tmp_path / "ep4.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test 4\n"
        "sortie: out/test4_final.mp4\n"
        "sequences:\n"
        f"  - rush: \"{rush}\"\n"
        "    sous_titres: aucun\n",
        encoding="utf-8",
    )

    out = pipeline.render_episode(episode_path, keep_intermediates=True)
    assert out.exists()
    assert (tmp_path / "out" / ".tmp_test4_final").exists()
