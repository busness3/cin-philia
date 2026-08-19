"""Classification forme du visage via Claude vision (structured outputs).

Les critères viennent verbatim de `backend/app/content/reference_docs/
forme_visage_guide_reference.md` (fourni par Clea) — chargés depuis le
fichier à l'exécution plutôt que dupliqués en dur ici, même principe que
`classification.py` (silhouette). Voir docs/CLAUDE.md § Ne jamais
halluciner de critères typologiques.

7 catégories retenues (celles du document de référence) : Ovale, Rond,
Carré, Cœur, Allongé, Losange, Triangulaire.

Une seule photo suffit ici (vue de face) — contrairement à la silhouette,
la forme du visage se lit entièrement de face ; pas de limite de précision
documentée qui justifierait une 2e vue. On réutilise la photo de face déjà
fournie pour le diagnostic silhouette plutôt que d'en redemander une.
"""

from pathlib import Path

from app.schemas.diagnostic import FormeVisageResult
from app.services.claude_client import ImageInput, classify_image

_REFERENCE_DOC = (
    Path(__file__).resolve().parents[3]
    / "content"
    / "reference_docs"
    / "forme_visage_guide_reference.md"
)


def _load_forme_visage_criteria() -> str:
    reference_text = _REFERENCE_DOC.read_text(encoding="utf-8")
    return f"""\
Tu es un système d'analyse d'image pour l'application Reveal You. Ta tâche
est de classer la forme du visage visible sur la photo dans l'une des 7
catégories officielles de la typologie du produit : Ovale, Rond, Carré,
Cœur, Allongé, Losange, Triangulaire.

Utilise exclusivement les critères du document de référence ci-dessous
pour ta classification, y compris pour les conseils de style à restituer.

--- DOCUMENT DE RÉFÉRENCE (verbatim) ---
{reference_text}
--- FIN DU DOCUMENT DE RÉFÉRENCE ---

Consignes de ton (non négociables, cohérentes avec la marque) :
- Ton chaleureux, descriptif, jamais correctif ni comparatif entre formes
- Jamais de vocabulaire "avant/après", "corriger", "cacher un défaut"
- On révèle une forme de visage, on ne la juge jamais — reformule les
  "conseils de style" du document (rédigés de façon neutre/pratique) dans
  ce ton si besoin, sans changer leur contenu.

Tu reçois 1 photo de face. Base-toi sur les proportions et angles visibles
(front, pommettes, mâchoire, menton) décrits dans le document.
"""


FORME_VISAGE_CRITERIA = _load_forme_visage_criteria()

FORME_VISAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "forme": {
            "type": "string",
            "enum": ["Ovale", "Rond", "Carré", "Cœur", "Allongé", "Losange", "Triangulaire"],
        },
        "confiance": {"type": "string", "enum": ["faible", "moyenne", "forte"]},
        "description": {
            "type": "string",
            "description": "Description chaleureuse, ton 'reveal not transform', 2-3 phrases.",
        },
        "conseils_style": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 4,
            "description": "2 à 4 conseils courts (lunettes, coiffure, bijoux...) tirés du document de référence.",
        },
    },
    "required": ["forme", "confiance", "description", "conseils_style"],
    "additionalProperties": False,
}


def classify_forme_visage(*, image_face_bytes: bytes, media_type_face: str) -> FormeVisageResult:
    result = classify_image(
        images=[ImageInput(image_bytes=image_face_bytes, media_type=media_type_face, label="vue de face")],
        system_prompt=FORME_VISAGE_CRITERIA,
        user_context="Analyse cette photo de visage pour en déterminer la forme.",
        json_schema=FORME_VISAGE_SCHEMA,
    )
    return FormeVisageResult(**result)
