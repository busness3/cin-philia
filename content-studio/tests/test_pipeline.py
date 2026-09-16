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


def test_render_episode_end_to_end_with_opening_band_and_cover(tmp_path, monkeypatch):
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
    # couverture générée à côté de la vidéo (reprend le texte de l'accroche)
    assert (tmp_path / "out" / "test_final_couverture.png").exists()


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
