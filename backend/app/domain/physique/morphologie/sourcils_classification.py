"""Classification forme des sourcils via Claude vision (structured outputs).

Les critères viennent verbatim de `backend/app/content/reference_docs/
sourcils_guide_reference.md` (fourni par Clea) — chargés depuis le fichier
à l'exécution, même principe que les autres classifieurs morphologie
(silhouette, forme du visage, forme des yeux). Voir docs/CLAUDE.md § Ne
jamais halluciner de critères typologiques.

6 catégories retenues (celles du document de référence) : Arqués, Droits,
Arrondis, Épais, Fins, En pente descendante.

⚠️ Le document source formule la catégorie "En pente descendante" dans un
vocabulaire plus correctif que le reste ("air fatigué", "corriger") — à
l'opposé de la charte de ton du produit. Le contenu est chargé verbatim
(fidélité à la source), mais le prompt ci-dessous demande explicitement à
Claude de reformuler sans jugement ni vocabulaire correctif, cohérent avec
le traitement des autres catégories morphologie.

Une seule photo suffit (vue de face), même principe que la forme du
visage et la forme des yeux.
"""

from pathlib import Path

from app.schemas.diagnostic import SourcilsResult
from app.services.claude_client import ImageInput, classify_image

_REFERENCE_DOC = (
    Path(__file__).resolve().parents[3]
    / "content"
    / "reference_docs"
    / "sourcils_guide_reference.md"
)


def _load_sourcils_criteria() -> str:
    reference_text = _REFERENCE_DOC.read_text(encoding="utf-8")
    return f"""\
Tu es un système d'analyse d'image pour l'application Reveal You. Ta tâche
est de classer la forme des sourcils visible sur la photo dans l'une des 6
catégories officielles de la typologie du produit : Arqués, Droits,
Arrondis, Épais, Fins, En pente descendante.

Utilise exclusivement les critères du document de référence ci-dessous
pour ta classification, y compris pour les conseils de style à restituer.

--- DOCUMENT DE RÉFÉRENCE (verbatim) ---
{reference_text}
--- FIN DU DOCUMENT DE RÉFÉRENCE ---

Consignes de ton (non négociables, cohérentes avec la marque) :
- Ton chaleureux, descriptif, jamais correctif ni comparatif entre formes
- Jamais de vocabulaire "avant/après", "corriger", "cacher un défaut", et
  jamais de jugement implicite (ex. ne jamais dire qu'une forme donne un
  air "fatigué" ou "triste", même si le document source le mentionne pour
  la catégorie "En pente descendante" — reformule entièrement sans ce
  jugement, en gardant uniquement l'information descriptive et les
  conseils d'entretien pratiques)
- On révèle une forme de sourcils, on ne la juge jamais — reformule les
  "conseils de style" du document (rédigés de façon neutre/pratique,
  parfois correctifs) dans ce ton, sans changer leur intention pratique.

Tu reçois 1 photo de face. Base-toi sur la forme, l'épaisseur et
l'inclinaison des sourcils décrites dans le document.
"""


SOURCILS_CRITERIA = _load_sourcils_criteria()

SOURCILS_SCHEMA = {
    "type": "object",
    "properties": {
        "forme": {
            "type": "string",
            "enum": ["Arqués", "Droits", "Arrondis", "Épais", "Fins", "En pente descendante"],
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
            "maxItems": 3,
            "description": "2 à 3 conseils courts (entretien, maquillage sourcils...) tirés du document de référence.",
        },
    },
    "required": ["forme", "confiance", "description", "conseils_style"],
    "additionalProperties": False,
}


def classify_sourcils(*, image_face_bytes: bytes, media_type_face: str) -> SourcilsResult:
    result = classify_image(
        images=[ImageInput(image_bytes=image_face_bytes, media_type=media_type_face, label="vue de face")],
        system_prompt=SOURCILS_CRITERIA,
        user_context="Analyse cette photo de visage pour en déterminer la forme des sourcils.",
        json_schema=SOURCILS_SCHEMA,
    )
    return SourcilsResult(**result)
