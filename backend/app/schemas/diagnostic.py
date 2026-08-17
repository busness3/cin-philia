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
    couleur_cheveux: str = Field(..., description="Description libre, ex: 'châtain foncé'")


class ColorimetrieResult(BaseModel):
    saison: str
    sous_saison: str | None = None
    palette: list[str] = Field(default_factory=list, description="Codes hex de la palette révélée")
    confiance: str = Field(
        default="forte",
        description=(
            "'faible' pour les combinaisons undertone neutre — la table de "
            "correspondance est un brouillon non validé pour ces cas, voir "
            "content/reference_docs/colorimetrie_saisons_brouillon.md"
        ),
    )


class MorphologieResult(BaseModel):
    silhouette_type: str
    confiance: str
    description: str = Field(..., description="Texte généré, ton 'reveal not transform'")
