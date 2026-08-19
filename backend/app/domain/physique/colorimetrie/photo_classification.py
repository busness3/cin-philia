"""Détermination undertone + contraste à partir de 2 photos (Claude vision).

Design volontaire : Claude ne calcule PAS la saison directement depuis les
photos. Son unique rôle ici est de lire, sur les images, les deux mêmes
valeurs catégorielles que le formulaire déclaratif collecte (undertone,
niveau_contraste) — dans le vocabulaire exact du document de référence de
Clea. Le calcul de la saison reste ensuite fait par
`app.domain.physique.colorimetrie.rules.determine_season()`, le même
moteur déterministe et testé qui sert le formulaire. Ça évite de dupliquer
la logique de correspondance saison à deux endroits.

Les définitions d'undertone et de contraste viennent verbatim de
`backend/app/content/reference_docs/typologie_pilier_physique.md` (§4 et
§8) — chargées depuis le fichier, pas dupliquées en dur.

⚠️ Pourquoi 2 photos plutôt qu'une : la lecture d'undertone depuis une
photo est sensible à l'éclairage, à la balance des blancs de l'appareil
et au maquillage (limite connue, cohérente avec la pratique professionnelle
de color analysis, qui utilise plusieurs tests). 2 photos permettent à
Claude de croiser ses lectures : cohérentes entre elles → confiance forte,
divergentes → confiance faible et on le dit explicitement plutôt que de
trancher au hasard.
"""

from pathlib import Path

from app.schemas.diagnostic import NiveauContraste, Undertone
from app.services.claude_client import ImageInput, classify_image

_CONTENT_DIR = Path(__file__).resolve().parents[3] / "content" / "reference_docs"
_REFERENCE_DOC = _CONTENT_DIR / "typologie_pilier_physique.md"
# Détail complet (définitions + exemples concrets) pour le contraste — le
# §4 de typologie_pilier_physique.md n'en donne qu'un résumé en 3 lignes.
_CONTRASTE_REFERENCE_DOC = _CONTENT_DIR / "contraste_guide_reference.md"


def _load_criteria() -> str:
    reference_text = _REFERENCE_DOC.read_text(encoding="utf-8")
    contraste_reference_text = _CONTRASTE_REFERENCE_DOC.read_text(encoding="utf-8")
    return f"""\
Tu es un système d'analyse d'image pour l'application Reveal You. Ta tâche
est de lire, sur les 2 photos de visage fournies, deux caractéristiques
précises : le sous-ton de peau (undertone) et le niveau de contraste
entre peau/yeux/cheveux — dans le vocabulaire exact défini ci-dessous.

Tu ne dois PAS calculer de saison colorielle toi-même — seulement
rapporter ces deux observations. Un autre système déterministe s'occupe
ensuite de la correspondance vers la saison.

--- DOCUMENT DE RÉFÉRENCE (verbatim) ---
{reference_text}
--- FIN DU DOCUMENT DE RÉFÉRENCE ---

--- DOCUMENT DE RÉFÉRENCE COMPLÉMENTAIRE SUR LE CONTRASTE (verbatim, avec exemples concrets) ---
{contraste_reference_text}
--- FIN DU DOCUMENT COMPLÉMENTAIRE ---

Consignes :
- undertone : "chaud", "froid" ou "neutre" (§8 du document)
- niveau_contraste : "faible", "moyen" ou "fort" (§4 du document)
- Tu reçois 2 photos, idéalement prises dans des conditions différentes
  (lumière, moment de la journée). Lis chaque photo indépendamment, puis
  rends un résultat unique :
  - si les 2 lectures s'accordent → confiance "forte"
  - si elles divergent, ou si une des deux photos a un éclairage
    artificiel/mixte qui rend la lecture incertaine → confiance "faible",
    et explique-le dans la justification (ce n'est jamais une faute de
    l'utilisatrice, juste une limite de l'analyse par photo)
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


def classify_undertone_contraste(
    *,
    image_1_bytes: bytes,
    media_type_1: str,
    image_2_bytes: bytes,
    media_type_2: str,
) -> dict:
    """Retourne un dict avec undertone/niveau_contraste/confiance/justification.

    Les valeurs `undertone`/`niveau_contraste` sont directement compatibles
    avec `app.schemas.diagnostic.ColorimetrieInput` (mêmes enums).
    """
    return classify_image(
        images=[
            ImageInput(image_bytes=image_1_bytes, media_type=media_type_1, label="photo 1"),
            ImageInput(image_bytes=image_2_bytes, media_type=media_type_2, label="photo 2"),
        ],
        system_prompt=UNDERTONE_CONTRASTE_CRITERIA,
        user_context="Analyse ces 2 photos de visage.",
        json_schema=UNDERTONE_CONTRASTE_SCHEMA,
    )
