"""Modèles de configuration (pydantic).

Architecture v2, alignée sur le document de DA globale du compte
« petit boucan » : la quasi-totalité de l'identité visuelle (palette, typo,
style des sous-titres, gabarit de couverture, timing d'ouverture/sortie) est
**globale et non négociable**. Une série ne peut surcharger que sa couleur
d'accent, plus des métadonnées de production qui ne pilotent pas le rendu
(tenue, décor, structure de script...).

- `configs/global.yaml`   -> GlobalConfig  : tout le socle DA + technique.
- `configs/series/*.yaml` -> SeriesConfig  : accent + métadonnées d'une série.
- `episodes/*.yaml`       -> EpisodeConfig : contenu concret d'une vidéo.
"""
from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

HEX_RE = re.compile(r"^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$")


def _check_hex(v: str) -> str:
    if not isinstance(v, str) or not HEX_RE.match(v):
        raise ValueError(f"couleur invalide {v!r}, attendu un format #RRGGBB")
    return v


# ---------------------------------------------------------------------------
# Config globale — identité TikTok commune (non négociable par série, sauf
# mention explicite « défini par la série »)
# ---------------------------------------------------------------------------


class Watermark(BaseModel):
    """Logo/watermark image, optionnel — absent du document de DA actuel
    (section 4 : « pas de logo, pas de tampon »), désactivé par défaut."""

    actif: bool = False
    image: Optional[str] = None
    position: Literal["haut_gauche", "haut_droite", "bas_gauche", "bas_droite"] = "haut_droite"
    opacite: float = 0.85
    marge_px: int = 24


class Identite(BaseModel):
    nom_compte: str = "petit boucan"
    bio: str = ""
    watermark: Watermark = Field(default_factory=Watermark)
    couleurs_marque: dict[str, str] = Field(
        default_factory=lambda: {
            "creme": "#F5EFE6",
            "chocolat": "#4A3328",
        }
    )

    @field_validator("couleurs_marque")
    @classmethod
    def _valide_couleurs(cls, v: dict[str, str]) -> dict[str, str]:
        return {k: _check_hex(c) for k, c in v.items()}


class ZoneSure(BaseModel):
    """Marges à ne pas couvrir par du texte/overlay (UI TikTok + rognage grille)."""

    haut_px: int = 220
    bas_px: int = 480  # l'UI TikTok recouvre les ~480 derniers pixels
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


class FontSpec(BaseModel):
    """Police = nom de fichier (sans extension) dans assets/fonts/."""

    police: str
    taille_px: int
    interligne_px: Optional[int] = None


class FontsConfig(BaseModel):
    titre: FontSpec = Field(
        default_factory=lambda: FontSpec(police="ArchivoNarrow-SemiBold", taille_px=96, interligne_px=104)
    )
    sous_titre: FontSpec = Field(default_factory=lambda: FontSpec(police="Archivo-Medium", taille_px=64))


class SousTitresConfig(BaseModel):
    """Style des sous-titres — global, non surchargeable par série (doc DA §11).

    Texte intégré directement sur l'image (pas de fond) : un contour assure
    la lisibilité sur n'importe quel plan. Pas d'animation, pas de
    surlignage mot par mot.
    """

    police: str = "Archivo-Medium"
    taille_px: int = 64
    couleur_texte: str = "#4A3328"
    couleur_contour: str = "#F5EFE6"
    epaisseur_contour: int = 3
    baseline_y_px: int = 1250
    max_lignes: int = 2
    # "segments" : découpage par phrases naturelles (whisper) — lecture posée,
    # correspond à la consigne « pas de légendes punchy ».
    # "groupes_mots" : paquets de N mots (gardé disponible pour un usage futur
    # hors de cette DA, mais non utilisé par les séries actuelles).
    mode_groupement: Literal["segments", "groupes_mots"] = "segments"
    mots_par_groupe: int = 6

    @field_validator("couleur_texte", "couleur_contour")
    @classmethod
    def _valide(cls, v: str) -> str:
        return _check_hex(v)


class BandeauConfig(BaseModel):
    x: int = 0
    y: int = 1140
    largeur: int = 1080
    hauteur: int = 360
    couleur_fond: str = "#F5EFE6"

    @field_validator("couleur_fond")
    @classmethod
    def _valide(cls, v: str) -> str:
        return _check_hex(v)


class BlocAccentConfig(BaseModel):
    x: int = 72
    y: int = 1200
    largeur: int = 18
    hauteur: int = 120


class TitreCouvertureConfig(BaseModel):
    x: int = 138
    baseline_ligne1_y: int = 1260
    baseline_ligne2_y: int = 1364
    largeur_max_px: int = 870
    max_lignes: int = 2
    max_mots: int = 4
    couleur_texte: str = "#4A3328"

    @field_validator("couleur_texte")
    @classmethod
    def _valide(cls, v: str) -> str:
        return _check_hex(v)


class GabaritCouverture(BaseModel):
    """Gabarit partagé par la couverture statique ET le bandeau incrusté en
    ouverture/sortie de vidéo (même bandeau, même police, même position)."""

    bandeau: BandeauConfig = Field(default_factory=BandeauConfig)
    bloc_accent: BlocAccentConfig = Field(default_factory=BlocAccentConfig)
    titre: TitreCouvertureConfig = Field(default_factory=TitreCouvertureConfig)


class TimingConfig(BaseModel):
    titre_apparition_s: float = 0.3
    titre_duree_s: float = 2.0
    sortie_duree_s: float = 2.0
    musique_apres_voix: bool = True
    # section 7 : sortie fixe « à tester avant généralisation » — coupe-circuit facile
    sortie_activee: bool = True


class MusiqueGlobalConfig(BaseModel):
    volume_defaut_db: float = -18.0
    ducking_sous_voix_db: float = -12.0


class SfxGlobalConfig(BaseModel):
    volume_defaut_db: float = -6.0


class AudioGlobalConfig(BaseModel):
    loudness_cible_lufs: float = -14.0
    musique: MusiqueGlobalConfig = Field(default_factory=MusiqueGlobalConfig)
    sfx: SfxGlobalConfig = Field(default_factory=SfxGlobalConfig)


class RythmeConfig(BaseModel):
    """Global, non exposé par série (le document de DA ne prévoit pas de
    rythme différencié — « peu de plans par vidéo » est une contrainte
    transverse, cf. §9)."""

    transition_defaut: Literal["cut", "fade", "slide", "zoom"] = "cut"
    duree_transition_ms: int = 200


class GlobalConfig(BaseModel):
    identite: Identite = Field(default_factory=Identite)
    video: VideoConfig = Field(default_factory=VideoConfig)
    fonts: FontsConfig = Field(default_factory=FontsConfig)
    sous_titres: SousTitresConfig = Field(default_factory=SousTitresConfig)
    couverture: GabaritCouverture = Field(default_factory=GabaritCouverture)
    timing: TimingConfig = Field(default_factory=TimingConfig)
    rythme: RythmeConfig = Field(default_factory=RythmeConfig)
    audio: AudioGlobalConfig = Field(default_factory=AudioGlobalConfig)


# ---------------------------------------------------------------------------
# Overlays génériques (cadre / watermark texte) — pas utilisés par la DA
# actuelle (pas de cadre, pas de tampon de série), mais gardés disponibles :
# la brique overlays.py reste utilisable telle quelle si une série future en
# a besoin.
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Config par série — réduite à l'accent + métadonnées de production (doc DA §11)
# ---------------------------------------------------------------------------


class AudioSerieConfig(BaseModel):
    """Mood par défaut de la série, à titre indicatif — la musique n'est
    ajoutée à une vidéo que si son episode.yaml le demande explicitement
    (`audio.musique` ou `audio.mood_musique`) : pas de musique automatique."""

    mood_musique: str = "neutre"
    volume_musique_db: float = -20.0
    sfx_transition: Optional[str] = None


class SeriesConfig(BaseModel):
    id: str
    nom: str
    description: str = ""

    # Seul override visuel autorisé (doc DA §2 et §11).
    accent: str = "#D42A2A"

    # Métadonnées de production — informatives, ne pilotent pas le rendu
    # (sauf cta_sortie, affiché dans le bandeau de sortie).
    tenue: str = ""
    decor: str = ""
    structure_script: str = ""
    duree_cible_s: Optional[float] = None
    cta_sortie: str = ""
    formule_titre: str = ""

    audio: AudioSerieConfig = Field(default_factory=AudioSerieConfig)

    @field_validator("accent")
    @classmethod
    def _valide_accent(cls, v: str) -> str:
        return _check_hex(v)


class ResolvedConfig(BaseModel):
    """Config globale + config série fusionnées, prêtes à consommer par le pipeline."""

    global_: GlobalConfig
    serie: SeriesConfig

    model_config = {"arbitrary_types_allowed": True}

    def couleur(self, cle: str, defaut: Optional[str] = None) -> str:
        """`"accent"` -> celui de la série ; toute autre clé -> charte globale
        (creme/chocolat)."""
        if cle == "accent":
            return self.serie.accent
        if cle in self.global_.identite.couleurs_marque:
            return self.global_.identite.couleurs_marque[cle]
        if defaut is not None:
            return defaut
        raise KeyError(f"couleur {cle!r} introuvable (ni accent série, ni charte globale)")


# ---------------------------------------------------------------------------
# Config épisode (contenu concret)
# ---------------------------------------------------------------------------


class Accroche(BaseModel):
    """Titre incrusté sur le plan d'ouverture (pas un carton séparé) — la
    durée/l'instant d'apparition sont fixés globalement (`timing`)."""

    texte: str


class CoverEpisodeConfig(BaseModel):
    """Couverture statique de la vidéo (gabarit `couverture` de la config
    globale). Le titre reprend celui de l'accroche si non précisé ici."""

    texte: Optional[str] = None
    temps_capture_s: float = 0.5


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
    """Musique optionnelle, opt-in par vidéo — pas de musique par défaut
    (toutes les vidéos n'en ont pas besoin). Renseigner `musique` (chemin
    explicite) ou `mood_musique` (pioche dans la bibliothèque) pour en
    ajouter à CETTE vidéo."""

    musique: Optional[str] = None
    mood_musique: Optional[str] = None
    sfx: list[SfxCue] = Field(default_factory=list)


class EpisodeConfig(BaseModel):
    serie: str
    titre_episode: str
    sortie: str
    accroche: Optional[Accroche] = None
    couverture: Optional[CoverEpisodeConfig] = None
    sequences: list[Sequence]
    audio: AudioEpisodeConfig = Field(default_factory=AudioEpisodeConfig)
