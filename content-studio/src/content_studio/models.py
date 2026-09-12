"""Modèles de configuration (pydantic).

Deux niveaux de config, dans configs/ :
- `configs/global.yaml`  -> GlobalConfig  : identité TikTok commune à toutes les
  séries (résolution, watermark, safe zone, loudness...).
- `configs/series/*.yaml` -> SeriesConfig : direction artistique propre à une
  série (couleurs, typo, style des sous-titres, rythme, ambiance audio...).

Et un niveau "contenu", dans episodes/ :
- `episodes/*.yaml` -> EpisodeConfig : un épisode concret = quels rushs, dans
  quel ordre, avec quelles accroches/overlays/sfx spécifiques.

Tous les champs ont des valeurs par défaut raisonnables : un fichier de série
peut se limiter à `id` + `nom` + les 2-3 réglages qu'on veut changer.
"""
from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

HEX_RE = re.compile(r"^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$")


class HexColorModel(BaseModel):
    """Mixin utilitaire : valide que les champs couleur sont bien en #RRGGBB."""

    @field_validator("*", mode="before")
    @classmethod
    def _noop(cls, v):  # pragma: no cover - placeholder pour sous-classes
        return v


def _check_hex(v: str) -> str:
    if not isinstance(v, str) or not HEX_RE.match(v):
        raise ValueError(f"couleur invalide {v!r}, attendu un format #RRGGBB")
    return v


# ---------------------------------------------------------------------------
# Config globale (identité TikTok commune)
# ---------------------------------------------------------------------------


class Watermark(BaseModel):
    actif: bool = False
    image: Optional[str] = None
    position: Literal["haut_gauche", "haut_droite", "bas_gauche", "bas_droite"] = "haut_droite"
    opacite: float = 0.85
    marge_px: int = 24


class Identite(BaseModel):
    nom_compte: str = ""
    watermark: Watermark = Field(default_factory=Watermark)
    police_principale: str = "Montserrat-Bold"
    couleurs_marque: dict[str, str] = Field(
        default_factory=lambda: {
            "accent": "#FF3B5C",
            "texte_clair": "#FFFFFF",
            "texte_sombre": "#111111",
        }
    )

    @field_validator("couleurs_marque")
    @classmethod
    def _valide_couleurs(cls, v: dict[str, str]) -> dict[str, str]:
        return {k: _check_hex(c) for k, c in v.items()}


class ZoneSure(BaseModel):
    """Marges à ne pas couvrir par du texte/overlay (boutons/UI TikTok)."""

    haut_px: int = 220
    bas_px: int = 320
    lateral_px: int = 40


class VideoConfig(BaseModel):
    largeur: int = 1080
    hauteur: int = 1920
    fps: int = 30
    codec_video: str = "libx264"
    crf: int = 18
    preset: str = "medium"
    codec_audio: str = "aac"
    bitrate_audio: str = "192k"
    zone_sure: ZoneSure = Field(default_factory=ZoneSure)


class MusiqueGlobalConfig(BaseModel):
    volume_defaut_db: float = -18.0
    ducking_sous_voix_db: float = -12.0


class SfxGlobalConfig(BaseModel):
    volume_defaut_db: float = -6.0


class AudioGlobalConfig(BaseModel):
    loudness_cible_lufs: float = -14.0
    musique: MusiqueGlobalConfig = Field(default_factory=MusiqueGlobalConfig)
    sfx: SfxGlobalConfig = Field(default_factory=SfxGlobalConfig)


class GlobalConfig(BaseModel):
    identite: Identite = Field(default_factory=Identite)
    video: VideoConfig = Field(default_factory=VideoConfig)
    audio: AudioGlobalConfig = Field(default_factory=AudioGlobalConfig)


# ---------------------------------------------------------------------------
# Config par série (direction artistique)
# ---------------------------------------------------------------------------


class SousTitresStyle(BaseModel):
    police: str = "Montserrat-SemiBold"
    taille_px: int = 68
    couleur_texte: str = "#FFFFFF"
    couleur_contour: str = "#000000"
    epaisseur_contour: int = 3
    couleur_mot_actif: Optional[str] = None
    position: Literal["bas_centre", "centre", "haut_centre"] = "bas_centre"
    marge_verticale_px: int = 340
    majuscules: bool = True
    mots_par_groupe: int = 3
    animation: Literal["pop", "fade", "slide_up", "none"] = "pop"
    duree_animation_ms: int = 120

    @field_validator("couleur_texte", "couleur_contour")
    @classmethod
    def _valide(cls, v: str) -> str:
        return _check_hex(v)

    @field_validator("couleur_mot_actif")
    @classmethod
    def _valide_opt(cls, v: Optional[str]) -> Optional[str]:
        return _check_hex(v) if v else v


class TitresStyle(BaseModel):
    style: Literal["carton_plein", "overlay_transparent"] = "carton_plein"
    police: str = "Montserrat-Bold"
    taille_px: int = 96
    couleur_texte: str = "#FFFFFF"
    couleur_fond: str = "#111111"
    animation_entree: Literal["slide_up", "fade", "zoom", "none"] = "slide_up"
    animation_sortie: Literal["fade", "slide_down", "none"] = "fade"
    duree_ms: int = 1800

    @field_validator("couleur_texte", "couleur_fond")
    @classmethod
    def _valide(cls, v: str) -> str:
        return _check_hex(v)


class CadreOverlay(BaseModel):
    actif: bool = False
    couleur: str = "#FFFFFF"
    epaisseur_px: int = 10

    @field_validator("couleur")
    @classmethod
    def _valide(cls, v: str) -> str:
        return _check_hex(v)


class WatermarkSerie(BaseModel):
    actif: bool = False
    texte: str = ""
    position: Literal["haut_gauche", "haut_droite", "bas_gauche", "bas_droite"] = "haut_gauche"


class OverlaysConfig(BaseModel):
    cadre: CadreOverlay = Field(default_factory=CadreOverlay)
    watermark_serie: WatermarkSerie = Field(default_factory=WatermarkSerie)


class RythmeConfig(BaseModel):
    duree_plan_min_s: float = 1.5
    duree_plan_max_s: float = 4.0
    transition_defaut: Literal["cut", "fade", "slide", "zoom"] = "cut"
    duree_transition_ms: int = 250


class AudioSerieConfig(BaseModel):
    mood_musique: str = "neutre"
    volume_musique_db: float = -20.0
    sfx_transition: Optional[str] = None


class SeriesConfig(BaseModel):
    id: str
    nom: str
    description: str = ""
    couleurs: dict[str, str] = Field(default_factory=dict)
    sous_titres: SousTitresStyle = Field(default_factory=SousTitresStyle)
    titres: TitresStyle = Field(default_factory=TitresStyle)
    overlays: OverlaysConfig = Field(default_factory=OverlaysConfig)
    rythme: RythmeConfig = Field(default_factory=RythmeConfig)
    audio: AudioSerieConfig = Field(default_factory=AudioSerieConfig)

    @field_validator("couleurs")
    @classmethod
    def _valide_couleurs(cls, v: dict[str, str]) -> dict[str, str]:
        return {k: _check_hex(c) for k, c in v.items()}


class ResolvedConfig(BaseModel):
    """Config globale + config série fusionnées, prêtes à consommer par le pipeline."""

    global_: GlobalConfig
    serie: SeriesConfig

    model_config = {"arbitrary_types_allowed": True}

    def couleur(self, cle: str, defaut: Optional[str] = None) -> str:
        """Couleur de la série si définie, sinon fallback sur la charte globale."""
        if cle in self.serie.couleurs:
            return self.serie.couleurs[cle]
        if cle in self.global_.identite.couleurs_marque:
            return self.global_.identite.couleurs_marque[cle]
        if defaut is not None:
            return defaut
        raise KeyError(f"couleur {cle!r} introuvable dans la série ni la charte globale")


# ---------------------------------------------------------------------------
# Config épisode (contenu concret)
# ---------------------------------------------------------------------------


class Accroche(BaseModel):
    texte: str
    duree_s: float = 2.0


class OverlayTexte(BaseModel):
    texte: str
    debut_s: float
    fin_s: float
    position: Literal[
        "haut_centre", "centre", "bas_centre", "haut_gauche", "haut_droite", "bas_gauche", "bas_droite"
    ] = "haut_centre"


class SfxCue(BaseModel):
    id: str
    au_temps_s: float
    volume_db: Optional[float] = None


class Sequence(BaseModel):
    rush: str
    debut_s: float = 0.0
    fin_s: Optional[float] = None
    sous_titres: str = "auto"  # "auto" (whisper) | "aucun" | chemin vers un .srt fourni
    overlay_texte: list[OverlayTexte] = Field(default_factory=list)
    transition_sortie: Optional[Literal["cut", "fade", "slide", "zoom"]] = None


class AudioEpisodeConfig(BaseModel):
    musique: Optional[str] = None  # chemin explicite, sinon pioché via mood_musique de la série
    sfx: list[SfxCue] = Field(default_factory=list)


class EpisodeConfig(BaseModel):
    serie: str
    titre_episode: str
    sortie: str
    accroche: Optional[Accroche] = None
    sequences: list[Sequence]
    audio: AudioEpisodeConfig = Field(default_factory=AudioEpisodeConfig)
