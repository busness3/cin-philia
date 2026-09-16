"""Tests de la brique config (chargement/validation YAML)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from content_studio import config  # noqa: E402
from content_studio.config import ConfigError  # noqa: E402
from content_studio.models import EpisodeConfig, SeriesConfig  # noqa: E402


def test_load_global_config():
    g = config.load_global_config()
    assert g.video.largeur == 1080
    assert g.video.hauteur == 1920
    assert g.identite.couleurs_marque["creme"].startswith("#")
    assert g.identite.couleurs_marque["chocolat"].startswith("#")
    assert g.sous_titres.mode_groupement == "segments"
    assert g.couverture.titre.max_mots == 4


def test_load_minimal_series_config(tmp_path, monkeypatch):
    # Une config de série minimale ne doit fournir que nom (+ éventuellement
    # accent) : tout le reste (métadonnées) a une valeur par défaut.
    series_dir = tmp_path / "series"
    series_dir.mkdir()
    (series_dir / "ma_serie.yaml").write_text("nom: Ma Série\naccent: \"#AA3300\"\n", encoding="utf-8")
    monkeypatch.setattr(config, "SERIES_DIR", series_dir)

    serie = config.load_series_config("ma_serie")
    assert serie.id == "ma_serie"
    assert serie.nom == "Ma Série"
    assert serie.accent == "#AA3300"
    assert serie.cta_sortie == ""


def test_series_config_invalid_accent_color(tmp_path, monkeypatch):
    series_dir = tmp_path / "series"
    series_dir.mkdir()
    (series_dir / "bad.yaml").write_text("nom: Bad\naccent: pas-une-couleur\n", encoding="utf-8")
    monkeypatch.setattr(config, "SERIES_DIR", series_dir)
    with pytest.raises(ConfigError):
        config.load_series_config("bad")


def test_resolved_config_couleur_accent(tmp_path, monkeypatch):
    series_dir = tmp_path / "series"
    series_dir.mkdir()
    (series_dir / "s1.yaml").write_text("nom: S1\naccent: \"#123456\"\n", encoding="utf-8")
    monkeypatch.setattr(config, "SERIES_DIR", series_dir)

    resolved = config.resolve_config("s1")
    assert resolved.couleur("accent") == "#123456"
    assert resolved.couleur("creme") == resolved.global_.identite.couleurs_marque["creme"]


def test_series_config_default_accent():
    serie = SeriesConfig.model_validate({"id": "x", "nom": "X"})
    assert serie.accent.startswith("#")  # valeur par défaut sensée, pas d'erreur


def test_series_config_override_accent():
    serie = SeriesConfig.model_validate({"id": "x", "nom": "X", "accent": "#00FF00"})
    assert serie.accent == "#00FF00"


def test_episode_config_minimal():
    ep = EpisodeConfig.model_validate({
        "serie": "diagnostic_serie",
        "titre_episode": "Test",
        "sortie": "out/test.mp4",
        "sequences": [{"rush": "rushs/x.mp4"}],
    })
    assert ep.sequences[0].sous_titres == "auto"
    assert ep.sequences[0].debut_s == 0.0
    assert ep.accroche is None
