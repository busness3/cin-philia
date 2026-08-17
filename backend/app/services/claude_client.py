"""Wrapper fin autour du SDK Anthropic officiel.

Règles de confidentialité appliquées ici :
- Aucune image (bytes/base64) n'est jamais loguée, même en cas d'erreur.
- Rien n'est écrit sur disque — la photo ne vit qu'en mémoire, le temps de
  l'appel HTTP vers l'API Claude, puis est immédiatement libérée par le GC
  une fois la fonction retournée.
- La clé API vient uniquement de la config (variable d'environnement) —
  jamais en dur dans le code.
"""

import base64
import json
import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

DEFAULT_MODEL = "claude-opus-5"


def classify_image(
    *,
    image_bytes: bytes,
    media_type: str,
    system_prompt: str,
    user_context: str,
    json_schema: dict,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Envoie une image + un contexte texte à Claude, contraint la réponse
    au schéma JSON fourni (structured outputs) et retourne le dict décodé.

    `system_prompt` doit contenir les critères de classification exacts
    (verbatim depuis les documents de référence produit) — ne jamais
    improviser de critères ici. Voir docs/CLAUDE.md § Ne jamais halluciner
    de critères typologiques.
    """
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    try:
        response = _client.messages.create(
            model=model,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    # Le prompt de critères est identique à chaque appel :
                    # mise en cache pour réduire le coût par diagnostic.
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": user_context},
                    ],
                }
            ],
            output_config={
                "format": {"type": "json_schema", "schema": json_schema}
            },
        )
    except anthropic.APIStatusError as exc:
        # On logue le statut/type d'erreur, jamais le contenu de la requête.
        logger.error("Échec de classification Claude (status=%s)", exc.status_code)
        raise

    text_block = next(b for b in response.content if b.type == "text")
    return json.loads(text_block.text)
