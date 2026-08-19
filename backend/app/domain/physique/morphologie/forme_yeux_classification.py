"""Classification forme des yeux via Claude vision (structured outputs).

Les critères viennent verbatim de `backend/app/content/reference_docs/
forme_yeux_guide_reference.md` (fourni par Clea) — chargés depuis le
fichier à l'exécution, même principe que `classification.py` (silhouette)
et `forme_visage_classification.py`. Voir docs/CLAUDE.md § Ne jamais
halluciner de critères typologiques.

9 catégories retenues (celles du document de référence) : Amande, Rond,
Tombant, Relevé, Monolide, Hooded, Rapprochés, Écartés, Protubérants.

⚠️ Note conservée pour une itération future : ces 9 catégories couvrent en
réalité 2 axes visuels différents — la FORME de l'œil (Amande, Rond,
Tombant, Relevé, Monolide, Hooded, Protubérants — 7 valeurs) et
l'ESPACEMENT entre les deux yeux (Rapprochés, Écartés — 2 valeurs), qui ne
sont pas mutuellement exclusifs (ex. une personne peut avoir des yeux en
amande ET rapprochés). Le document de référence de Clea les présente comme
une liste plate de 9 types (cohérent avec le framework produit : "Forme
des yeux — 9+ types"), donc on garde ce même choix unique en V1 plutôt que
d'inventer une structure à 2 axes non demandée. Si Clea veut distinguer
forme + espacement séparément, il faudra le valider explicitement (comme
pour le 3e axe colorimétrie).

Une seule photo suffit (vue de face), même principe que la forme du
visage.
"""

from pathlib import Path

from app.schemas.diagnostic import FormeYeuxResult
from app.services.claude_client import ImageInput, classify_image

_REFERENCE_DOC = (
    Path(__file__).resolve().parents[3]
    / "content"
    / "reference_docs"
    / "forme_yeux_guide_reference.md"
)


def _load_forme_yeux_criteria() -> str:
    reference_text = _REFERENCE_DOC.read_text(encoding="utf-8")
    return f"""\
Tu es un système d'analyse d'image pour l'application Reveal You. Ta tâche
est de classer la forme des yeux visible sur la photo dans l'une des 9
catégories officielles de la typologie du produit : Amande, Rond, Tombant,
Relevé, Monolide, Hooded, Rapprochés, Écartés, Protubérants.

Utilise exclusivement les critères du document de référence ci-dessous
pour ta classification, y compris pour les conseils de maquillage à
restituer. Ces 9 catégories couvrent 2 aspects différents (forme de l'œil
et espacement entre les yeux) qui peuvent techniquement coexister chez une
même personne — choisis la catégorie la plus nettement identifiable sur la
photo.

--- DOCUMENT DE RÉFÉRENCE (verbatim) ---
{reference_text}
--- FIN DU DOCUMENT DE RÉFÉRENCE ---

Consignes de ton (non négociables, cohérentes avec la marque) :
- Ton chaleureux, descriptif, jamais correctif ni comparatif entre formes
- Jamais de vocabulaire "avant/après", "corriger", "cacher un défaut"
- On révèle une forme de regard, on ne la juge jamais — reformule les
  "conseils de style" du document (rédigés de façon neutre/pratique) dans
  ce ton si besoin, sans changer leur contenu.

Tu reçois 1 photo de face. Base-toi sur la forme, la position des coins et
l'espacement des yeux décrits dans le document.
"""


FORME_YEUX_CRITERIA = _load_forme_yeux_criteria()

FORME_YEUX_SCHEMA = {
    "type": "object",
    "properties": {
        "forme": {
            "type": "string",
            "enum": [
                "Amande",
                "Rond",
                "Tombant",
                "Relevé",
                "Monolide",
                "Hooded",
                "Rapprochés",
                "Écartés",
                "Protubérants",
            ],
        },
        "confiance": {"type": "string", "enum": ["faible", "moyenne", "forte"]},
        "description": {
            "type": "string",
            "description": "Description chaleureuse, ton 'reveal not transform', 2-3 phrases.",
        },
        "conseils_maquillage": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 3,
            "description": "2 à 3 conseils courts (eyeliner, ombre à paupières...) tirés du document de référence.",
        },
    },
    "required": ["forme", "confiance", "description", "conseils_maquillage"],
    "additionalProperties": False,
}


def classify_forme_yeux(*, image_face_bytes: bytes, media_type_face: str) -> FormeYeuxResult:
    result = classify_image(
        images=[ImageInput(image_bytes=image_face_bytes, media_type=media_type_face, label="vue de face")],
        system_prompt=FORME_YEUX_CRITERIA,
        user_context="Analyse cette photo de visage pour en déterminer la forme des yeux.",
        json_schema=FORME_YEUX_SCHEMA,
    )
    return FormeYeuxResult(**result)
