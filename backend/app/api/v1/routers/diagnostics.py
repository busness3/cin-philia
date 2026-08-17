"""Endpoints de diagnostic.

Règle de confidentialité appliquée ici : le fichier image reçu (`UploadFile`)
n'est jamais écrit sur disque et n'est jamais loggé — il est lu en mémoire,
transmis à Claude pour classification, puis la variable sort de portée et
est récupérée par le garbage collector. Rien d'autre que le résultat
structuré ne sort de cette fonction.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.physique.colorimetrie.rules import determine_season
from app.domain.physique.morphologie.classification import classify_silhouette
from app.models.diagnostic_result import DiagnosticResult
from app.schemas.diagnostic import ColorimetrieInput, ColorimetrieResult, MorphologieResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/colorimetrie", response_model=ColorimetrieResult)
def diagnostic_colorimetrie(
    payload: ColorimetrieInput,
    user_id: str,
    db: Session = Depends(get_db),
) -> ColorimetrieResult:
    result = determine_season(payload)

    db.add(
        DiagnosticResult(
            user_id=user_id,
            category="colorimetrie",
            payload=result.model_dump(),
        )
    )
    db.commit()
    return result


@router.post("/morphologie/silhouette", response_model=MorphologieResult)
async def diagnostic_silhouette(
    user_id: str,
    mesures_declarees: str,
    db: Session = Depends(get_db),
    photo: UploadFile = File(...),
) -> MorphologieResult:
    if photo.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Format d'image non supporté.")

    image_bytes = await photo.read()  # lecture en mémoire uniquement — jamais écrit sur disque

    try:
        result = classify_silhouette(
            image_bytes=image_bytes,
            media_type=photo.content_type,
            mesures_declarees=mesures_declarees,
        )
    except Exception:
        logger.exception("Échec de la classification silhouette (user_id=%s)", user_id)
        raise HTTPException(status_code=502, detail="Échec de la classification.") from None
    # `image_bytes` sort de portée ici — jamais persisté, jamais loggé.

    db.add(
        DiagnosticResult(
            user_id=user_id,
            category="morphologie_silhouette",
            payload=result.model_dump(),
        )
    )
    db.commit()
    return result
