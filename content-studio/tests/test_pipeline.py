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


def _setup_project(tmp_path, monkeypatch, series_yaml: str = "nom: Test Serie\n"):
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


def test_render_episode_end_to_end_no_subtitles(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=2.0)

    episode_path = tmp_path / "ep.yaml"
    episode_path.write_text(
        "serie: test_serie\n"
        "titre_episode: Test\n"
        "sortie: out/test_final.mp4\n"
        "accroche:\n"
        "  texte: \"Salut à toutes\"\n"
        "  duree_s: 1.0\n"
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
    # accroche (1s) + rush (2s) en cut -> ~3s
    assert 2.5 < info.duration < 3.5
    # dossier de travail nettoyé
    assert not (tmp_path / "out" / ".tmp_test_final").exists()


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


def test_render_episode_with_overlays_and_cadre(tmp_path, monkeypatch):
    series_yaml = (
        "nom: Test Serie\n"
        "overlays:\n"
        "  cadre:\n"
        "    actif: true\n"
        "    couleur: \"#FF3B5C\"\n"
        "    epaisseur_px: 10\n"
        "  watermark_serie:\n"
        "    actif: true\n"
        "    texte: \"TEST SERIE\"\n"
        "    position: haut_gauche\n"
    )
    _setup_project(tmp_path, monkeypatch, series_yaml=series_yaml)
    rush = make_synthetic_clip(tmp_path / "rush1.mp4", width=640, height=360, duration=1.5)

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
