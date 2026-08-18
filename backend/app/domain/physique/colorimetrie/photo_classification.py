"""Détermination undertone + contraste à partir d'une photo (Claude vision).

Design volontaire : Claude ne calcule PAS la saison directement depuis la
photo. Son unique rôle ici est de lire, sur l'image, les deux mêmes
valeurs catégorielles que le formulaire déclaratif collecte (undertone,
niveau_contraste) — dans le vocabulaire exact du document de référence de
Clea. Le calcul de la saison reste ensuite fait par
`app.domain.physique.colorimetrie.rules.determine_season()`, le même
moteur déterministe et testé qui sert le formulaire. Ça évite de dupliquer
la logique de correspondance saison à deux endroits.

Les définitions d'undertone et de contraste viennent verbatim de
`backend/app/content/reference_docs/typologie_pilier_physique.md` (§4 et
§8) — chargées depuis le fichier, pas dupliquées en dur.

⚠️ Limite connue à documenter pour l'utilisatrice (cohérent avec la
pratique professionnelle de color analysis) : la lecture d'undertone
depuis une photo est sensible à l'éclairage, à la balance des blancs de
l'appareil et au maquillage — d'où la consigne de capture (lumière
naturelle, sans maquillage/filtre) et le champ `confiance` dans le
résultat.
"""

from pathlib import Path

from app.schemas.diagnostic import NiveauContraste, Undertone
from app.services.claude_client import classify_image

_REFERENCE_DOC = (
    Path(__file__).resolve().parents[3]
    / "content"
    / "reference_docs"
    / "typologie_pilier_physique.md"
)


def _load_criteria() -> str:
    reference_text = _REFERENCE_DOC.read_text(encoding="utf-8")
    return f"""\
Tu es un système d'analyse d'image pour l'application Reveal You. Ta tâche
est de lire, sur la photo de visage fournie, deux caractéristiques
précises : le sous-ton de peau (undertone) et le niveau de contraste
entre peau/yeux/cheveux — dans le vocabulaire exact défini ci-dessous.

Tu ne dois PAS calculer de saison colorielle toi-même — seulement
rapporter ces deux observations. Un autre système déterministe s'occupe
ensuite de la correspondance vers la saison.

--- DOCUMENT DE RÉFÉRENCE (verbatim) ---
{reference_text}
--- FIN DU DOCUMENT DE RÉFÉRENCE ---

Consignes :
- undertone : "chaud", "froid" ou "neutre" (§8 du document)
- niveau_contraste : "faible", "moyen" ou "fort" (§4 du document)
- confiance : ta confiance dans cette lecture. Marque "faible" si
  l'éclairage semble artificiel, mixte, ou si un maquillage/filtre rend la
  lecture incertaine — c'est une vraie limite de l'analyse par photo, pas
  une faute de l'utilisatrice.
- Ton chaleureux et descriptif dans la justification, jamais correctif —
  cohérent avec la marque (on décrit, on ne juge jamais).
"""


UNDERTONE_CONTRASTE_CRITERIA = _load_criteria()

UNDERTONE_CONTRASTE_SCHEMA = {
    "type": "object",
    "properties": {
        "undertone": {"type": "string", "enum": [u.value for u in Undertone]},
        "niveau_contraste": {"type": "string", "enum": [c.value for c in NiveauContraste]},
        "confiance": {"type": "string", "enum": ["faible", "moyenne", "forte"]},
        "justification": {
            "type": "string",
            "description": "1-2 phrases expliquant la lecture, ton descriptif non-correctif.",
        },
    },
    "required": ["undertone", "niveau_contraste", "confiance", "justification"],
    "additionalProperties": False,
}


def classify_undertone_contraste(*, image_bytes: bytes, media_type: str) -> dict:
    """Retourne un dict avec undertone/niveau_contraste/confiance/justification.

    Les valeurs `undertone`/`niveau_contraste` sont directement compatibles
    avec `app.schemas.diagnostic.ColorimetrieInput` (mêmes enums).
    """
    return classify_image(
        image_bytes=image_bytes,
        media_type=media_type,
        system_prompt=UNDERTONE_CONTRASTE_CRITERIA,
        user_context="Analyse cette photo de visage.",
        json_schema=UNDERTONE_CONTRASTE_SCHEMA,
    )
