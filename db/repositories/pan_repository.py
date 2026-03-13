import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.document_model import PanCardDetails
from schemas.document_schemas import PanCreate

logger = logging.getLogger(__name__)


def create_pan(
    db: Session,
    pan: PanCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system",
):
    existing = db.query(PanCardDetails).filter(
        PanCardDetails.pan_number == pan.pan_number
    ).first()

    if existing:
        logger.warning("PAN %s already exists in database.", pan.pan_number)
        raise HTTPException(
            status_code=400,
            detail="Data for this PAN card already exists in the database.",
        )

    db_pan = PanCardDetails(
        pan_number=pan.pan_number,
        full_name=pan.full_name,
        father_name=pan.father_name,
        date_of_birth=pan.date_of_birth,
        pan_type=pan.derive_pan_type(),
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_pan)
        db.commit()
        db.refresh(db_pan)
        logger.info("PAN %s saved successfully.", pan.pan_number)
        return db_pan
    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error while saving PAN %s", pan.pan_number)
        raise HTTPException(
            status_code=400,
            detail="Data for this PAN card already exists in the database.",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving PAN")
        raise HTTPException(status_code=500, detail=f"Failed to save PAN details: {str(exc)}")
