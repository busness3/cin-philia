"""Classification silhouette via Claude vision (structured outputs).

Les critères viennent verbatim de `backend/app/content/reference_docs/
silhouettes_guide_reference.md` (fourni par Clea) — chargés depuis le
fichier à l'exécution plutôt que dupliqués en dur ici, pour que toute
mise à jour du document de référence se propage sans toucher au code.
Voir docs/CLAUDE.md § Ne jamais halluciner de critères typologiques.

La typologie officielle V1 retient 5 catégories (H/A/V/O/X) — voir le
schéma de sortie ci-dessous. Le document de référence détaille aussi 2
variantes ("8", "Diamant/Ovale") non retenues en V1 ; on les exclut du
schéma mais on ne les cache pas au modèle, on lui dit explicitement de
ne pas les utiliser.
"""

from pathlib import Path

from app.schemas.diagnostic import MorphologieResult
from app.services.claude_client import classify_image

_REFERENCE_DOC = (
    Path(__file__).resolve().parents[3]
    / "content"
    / "reference_docs"
    / "silhouettes_guide_reference.md"
)


def _load_silhouette_criteria() -> str:
    reference_text = _REFERENCE_DOC.read_text(encoding="utf-8")
    return f"""\
Tu es un système d'analyse d'image pour l'application Reveal You. Ta tâche
est de classer la silhouette visible sur la photo dans l'une des 5
catégories officielles de la typologie du produit : H, A, V, O, X.

Utilise exclusivement les critères du document de référence ci-dessous
pour ta classification. Ce document mentionne aussi deux variantes ("8" et
"Diamant/Ovale") qui NE FONT PAS partie de la typologie V1 — ignore-les
pour la classification, ne renvoie jamais ces valeurs.

--- DOCUMENT DE RÉFÉRENCE (verbatim) ---
{reference_text}
--- FIN DU DOCUMENT DE RÉFÉRENCE ---

Consignes de ton (non négociables, cohérentes avec la marque) :
- Ton chaleureux, descriptif, jamais correctif ni comparatif entre types
- Jamais de vocabulaire "avant/après", "corriger", "cacher un défaut"
- On révèle une silhouette, on ne la juge jamais

Utilise les mesures déclarées par l'utilisatrice (si fournies) en
complément de l'analyse visuelle — approche hybride recommandée par le
produit, la classification à partir d'une seule image ayant une précision
limitée.
"""


SILHOUETTE_CRITERIA = _load_silhouette_criteria()

SILHOUETTE_SCHEMA = {
    "type": "object",
    "properties": {
        "silhouette_type": {"type": "string", "enum": ["H", "A", "V", "O", "X"]},
        "confiance": {"type": "string", "enum": ["faible", "moyenne", "forte"]},
        "description": {
            "type": "string",
            "description": "Description chaleureuse, ton 'reveal not transform', 2-3 phrases.",
        },
    },
    "required": ["silhouette_type", "confiance", "description"],
    "additionalProperties": False,
}


def classify_silhouette(*, image_bytes: bytes, media_type: str, mesures_declarees: str) -> MorphologieResult:
    result = classify_image(
        image_bytes=image_bytes,
        media_type=media_type,
        system_prompt=SILHOUETTE_CRITERIA,
        user_context=f"Mesures déclarées par l'utilisatrice : {mesures_declarees}",
        json_schema=SILHOUETTE_SCHEMA,
    )
    return MorphologieResult(**result)
