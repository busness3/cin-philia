"""Classification silhouette via Claude vision (structured outputs).

⚠️ TODO — bloqué en attente du document de référence de Clea :
`SILHOUETTE_CRITERIA` ci-dessous est un PLACEHOLDER. Il ne doit PAS être
utilisé en production tel quel — il faut y coller le contenu verbatim du
document de référence sur les types de silhouette (H/A/V/O/X) fourni par
Clea avant d'activer cet endpoint pour de vrai. Voir docs/CLAUDE.md
§ Ne jamais halluciner de critères typologiques.

Les 5 catégories (H, A, V, O, X) sont confirmées par le produit — seule la
description des critères distinctifs de chacune manque ici.
"""

from app.schemas.diagnostic import MorphologieResult
from app.services.claude_client import classify_image

# PLACEHOLDER — à remplacer par le contenu réel du document de Clea.
SILHOUETTE_CRITERIA = """\
Tu vas classifier une silhouette corporelle dans l'une des 5 catégories
suivantes : H, A, V, O, X.

[EN ATTENTE DU CONTENU DE RÉFÉRENCE — ne pas utiliser cette fonction en
production tant que ce texte n'a pas été remplacé par les critères réels]

Réponds uniquement dans le langage descriptif et non-correctif de la
marque : on décrit une silhouette, on ne la juge jamais, et on ne compare
jamais un type à un autre.
"""

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
