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
from app.domain.physique.colorimetrie.photo_classification import classify_undertone_contraste
from app.domain.physique.colorimetrie.rules import determine_season
from app.domain.physique.morphologie.classification import classify_silhouette
from app.domain.physique.morphologie.forme_visage_classification import classify_forme_visage
from app.domain.physique.morphologie.forme_yeux_classification import classify_forme_yeux
from app.models.diagnostic_result import DiagnosticResult
from app.schemas.diagnostic import ColorimetrieInput, ColorimetrieResult, MorphologieResult

logger = logging.getLogger(__name__)
router = APIRouter()

_SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def _read_photo(photo: UploadFile) -> bytes:
    if photo.content_type not in _SUPPORTED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Format d'image non supporté.")
    return await photo.read()  # lecture en mémoire uniquement — jamais écrit sur disque


def _save_result(db: Session, *, user_id: str, category: str, result) -> None:
    db.add(DiagnosticResult(user_id=user_id, category=category, payload=result.model_dump()))
    db.commit()


@router.post("/colorimetrie", response_model=ColorimetrieResult)
def diagnostic_colorimetrie(
    payload: ColorimetrieInput,
    user_id: str,
    db: Session = Depends(get_db),
) -> ColorimetrieResult:
    result = determine_season(payload)
    _save_result(db, user_id=user_id, category="colorimetrie", result=result)
    return result


@router.post("/colorimetrie/photo", response_model=ColorimetrieResult)
async def diagnostic_colorimetrie_photo(
    user_id: str,
    db: Session = Depends(get_db),
    photo_1: UploadFile = File(...),
    photo_2: UploadFile = File(...),
) -> ColorimetrieResult:
    """Variante photo du diagnostic colorimétrie — 2 photos (idéalement
    dans des conditions de lumière différentes) pour fiabiliser la lecture.
    Voir `photo_classification.py` pour le design (Claude lit undertone/
    contraste, le moteur de règles déterministe calcule ensuite la saison,
    exactement comme le parcours formulaire).
    """
    image_1_bytes = await _read_photo(photo_1)
    image_2_bytes = await _read_photo(photo_2)

    try:
        lecture = classify_undertone_contraste(
            image_1_bytes=image_1_bytes,
            media_type_1=photo_1.content_type,
            image_2_bytes=image_2_bytes,
            media_type_2=photo_2.content_type,
        )
    except Exception:
        logger.exception("Échec de la lecture undertone/contraste (user_id=%s)", user_id)
        raise HTTPException(status_code=502, detail="Échec de l'analyse de la photo.") from None
    # `image_1_bytes`/`image_2_bytes` sortent de portée ici — jamais persistés, jamais logués.

    result = determine_season(
        ColorimetrieInput(undertone=lecture["undertone"], niveau_contraste=lecture["niveau_contraste"])
    )
    # Confiance finale = la plus prudente des deux sources (lecture visuelle
    # Claude + incertitude connue de la table sur undertone neutre).
    if lecture["confiance"] != "forte":
        result.confiance = "faible"
    result.justification = lecture["justification"]

    _save_result(db, user_id=user_id, category="colorimetrie_photo", result=result)
    return result


@router.post("/morphologie/silhouette", response_model=MorphologieResult)
async def diagnostic_silhouette(
    user_id: str,
    mesures_declarees: str,
    db: Session = Depends(get_db),
    photo_face: UploadFile = File(...),
    photo_profil: UploadFile = File(...),
) -> MorphologieResult:
    image_face_bytes = await _read_photo(photo_face)
    image_profil_bytes = await _read_photo(photo_profil)

    try:
        result = classify_silhouette(
            image_face_bytes=image_face_bytes,
            media_type_face=photo_face.content_type,
            image_profil_bytes=image_profil_bytes,
            media_type_profil=photo_profil.content_type,
            mesures_declarees=mesures_declarees,
        )
    except Exception:
        logger.exception("Échec de la classification silhouette (user_id=%s)", user_id)
        raise HTTPException(status_code=502, detail="Échec de la classification.") from None

    try:
        # Réutilise la photo de face déjà fournie ci-dessus — pas de photo
        # supplémentaire demandée à l'utilisatrice pour cette 2e catégorie.
        result.forme_visage = classify_forme_visage(
            image_face_bytes=image_face_bytes,
            media_type_face=photo_face.content_type,
        )
    except Exception:
        # Non bloquant : le résultat silhouette reste utile seul si la
        # classification forme du visage échoue (ex. incident API ponctuel).
        logger.exception("Échec de la classification forme du visage (user_id=%s)", user_id)

    try:
        # Même photo de face, 3e catégorie combinée dans la même réponse.
        result.forme_yeux = classify_forme_yeux(
            image_face_bytes=image_face_bytes,
            media_type_face=photo_face.content_type,
        )
    except Exception:
        logger.exception("Échec de la classification forme des yeux (user_id=%s)", user_id)
    # `image_face_bytes`/`image_profil_bytes` sortent de portée ici — jamais persistés, jamais logués.

    _save_result(db, user_id=user_id, category="morphologie_silhouette", result=result)
    return result
