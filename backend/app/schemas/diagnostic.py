"""Schémas Pydantic des requêtes/réponses de diagnostic.

Note volontaire : aucun schéma ici ne transporte la photo au-delà de la
requête entrante — elle n'est jamais incluse dans une réponse ni dans un
modèle destiné à être persisté.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Undertone(str, Enum):
    CHAUD = "chaud"
    FROID = "froid"
    NEUTRE = "neutre"


class NiveauContraste(str, Enum):
    # Vocabulaire aligné sur le document de référence de Clea
    # (typologie_pilier_physique.md § Contraste) : "faible", pas "clair".
    FAIBLE = "faible"
    MOYEN = "moyen"
    FORT = "fort"


class ColorimetrieInput(BaseModel):
    undertone: Undertone
    niveau_contraste: NiveauContraste
    # Optionnel : collecté par le formulaire déclaratif, absent du parcours
    # photo (voir photo_classification.py). Note : n'est pas encore utilisé
    # par determine_season() — collecté pour un usage futur (ex. affiner
    # les sous-saisons), pas exploité dans la V1 4-saisons actuelle.
    couleur_cheveux: str | None = Field(default=None, description="Description libre, ex: 'châtain foncé'")


class ColorimetrieResult(BaseModel):
    saison: str
    sous_saison: str | None = None
    palette: list[str] = Field(default_factory=list, description="Codes hex de la palette révélée")
    confiance: str = Field(
        default="forte",
        description=(
            "'faible' pour les combinaisons undertone neutre, ou pour une "
            "lecture photo jugée incertaine par Claude (éclairage, "
            "maquillage...) — voir content/reference_docs/"
            "colorimetrie_saisons_brouillon.md"
        ),
    )
    justification: str | None = Field(
        default=None,
        description="Explication de la lecture undertone/contraste, uniquement sur le parcours photo.",
    )
    conseils_style: list[str] = Field(
        default_factory=list,
        description=(
            "Conseils de style combinant undertone (bijoux/métaux, couleurs) et "
            "niveau de contraste (association de couleurs, maquillage), issus de "
            "content/reference_docs/teint_soustons_guide_reference.md et "
            "contraste_guide_reference.md."
        ),
    )


class FormeVisageResult(BaseModel):
    forme: str
    confiance: str
    description: str = Field(..., description="Texte généré, ton 'reveal not transform'")
    conseils_style: list[str] = Field(
        default_factory=list,
        description="2-4 conseils courts (lunettes, coiffure, bijoux...) issus du document de référence.",
    )


class FormeYeuxResult(BaseModel):
    forme: str
    confiance: str
    description: str = Field(..., description="Texte généré, ton 'reveal not transform'")
    conseils_maquillage: list[str] = Field(
        default_factory=list,
        description="2-3 conseils courts (eyeliner, ombre à paupières...) issus du document de référence.",
    )


class SourcilsResult(BaseModel):
    forme: str
    confiance: str
    description: str = Field(..., description="Texte généré, ton 'reveal not transform'")
    conseils_style: list[str] = Field(
        default_factory=list,
        description="2-3 conseils courts (entretien, maquillage sourcils...) issus du document de référence.",
    )


class MorphologieResult(BaseModel):
    silhouette_type: str
    confiance: str
    description: str = Field(..., description="Texte généré, ton 'reveal not transform'")
    # Optionnels : absents si leur classification échoue alors que la
    # silhouette a réussi (voir diagnostics.py) — on ne fait pas échouer tout
    # l'endpoint pour ça, la silhouette reste utile seule.
    forme_visage: FormeVisageResult | None = None
    forme_yeux: FormeYeuxResult | None = None
    sourcils: SourcilsResult | None = None


class TypeTextureCheveux(str, Enum):
    """Méthode André Walker — voir content/reference_docs/
    nature_cheveux_guide_reference.md. Déclaratif uniquement (pas de
    classification photo) : décision de Clea, la lecture capillaire par
    photo demande une expertise qui reviendra dans une itération future."""

    T1A = "1A"
    T1B = "1B"
    T1C = "1C"
    T2A = "2A"
    T2B = "2B"
    T2C = "2C"
    T3A = "3A"
    T3B = "3B"
    T3C = "3C"
    T4A = "4A"
    T4B = "4B"
    T4C = "4C"


class NatureCheveuxInput(BaseModel):
    type_texture: TypeTextureCheveux


class NatureCheveuxResult(BaseModel):
    type_texture: str
    description: str = Field(..., description="Texte issu du document de référence (pas généré par IA).")
    conseils_style: list[str] = Field(
        default_factory=list,
        description="1-2 conseils d'entretien/coiffage issus du document de référence.",
    )
