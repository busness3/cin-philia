"""Chargement des fichiers YAML de config (global, série, épisode)."""
from __future__ import annotations

from pathlib import Path

import yaml

from .models import EpisodeConfig, GlobalConfig, ResolvedConfig, SeriesConfig

# Racine du projet content-studio (deux niveaux au-dessus de ce fichier :
# src/content_studio/config.py -> content-studio/)
ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = ROOT / "configs"
SERIES_DIR = CONFIGS_DIR / "series"
EPISODES_DIR = ROOT / "episodes"
SOUNDS_DIR = ROOT / "sounds"
ASSETS_DIR = ROOT / "assets"


class ConfigError(Exception):
    pass


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"fichier de config introuvable : {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_global_config(path: Path | None = None) -> GlobalConfig:
    path = path or (CONFIGS_DIR / "global.yaml")
    return GlobalConfig.model_validate(_load_yaml(path))


def load_series_config(series_id: str) -> SeriesConfig:
    path = SERIES_DIR / f"{series_id}.yaml"
    data = _load_yaml(path)
    data.setdefault("id", series_id)
    try:
        return SeriesConfig.model_validate(data)
    except Exception as e:  # pragma: no cover - message d'erreur pédagogique
        raise ConfigError(f"config série invalide ({path}) : {e}") from e


def resolve_config(series_id: str, global_path: Path | None = None) -> ResolvedConfig:
    """Charge et fusionne la config globale + la config d'une série."""
    return ResolvedConfig(global_=load_global_config(global_path), serie=load_series_config(series_id))


def load_episode(path: str | Path) -> EpisodeConfig:
    path = Path(path)
    if not path.is_absolute():
        # autorise un chemin relatif à episodes/ ou au cwd
        candidate = EPISODES_DIR / path
        path = candidate if candidate.exists() else path
    data = _load_yaml(path)
    try:
        return EpisodeConfig.model_validate(data)
    except Exception as e:  # pragma: no cover
        raise ConfigError(f"config épisode invalide ({path}) : {e}") from e


def list_series() -> list[str]:
    if not SERIES_DIR.exists():
        return []
    return sorted(p.stem for p in SERIES_DIR.glob("*.yaml"))
