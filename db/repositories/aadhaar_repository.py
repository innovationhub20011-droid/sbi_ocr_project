import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.document_model import AadhaarCardDetails
from schemas.document_schemas import AadhaarCreate

logger = logging.getLogger(__name__)


def create_aadhaar(
    db: Session,
    aadhaar: AadhaarCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system",
):
    existing = db.query(AadhaarCardDetails).filter(
        AadhaarCardDetails.aadhaar_number == aadhaar.aadhaar_number
    ).first()

    if existing:
        logger.warning("Aadhaar %s already exists in database.", aadhaar.aadhaar_number)
        raise HTTPException(
            status_code=400,
            detail="Data for this Aadhaar card already exists in the database.",
        )

    db_aadhaar = AadhaarCardDetails(
        aadhaar_number=aadhaar.aadhaar_number,
        full_name=aadhaar.full_name,
        date_of_birth=aadhaar.date_of_birth,
        gender=aadhaar.gender,
        address=aadhaar.address,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_aadhaar)
        db.commit()
        db.refresh(db_aadhaar)
        logger.info("Aadhaar %s saved successfully.", aadhaar.aadhaar_number)
        return db_aadhaar
    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error while saving Aadhaar %s", aadhaar.aadhaar_number)
        raise HTTPException(
            status_code=400,
            detail="Data for this Aadhaar card already exists in the database.",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving Aadhaar")
        raise HTTPException(status_code=500, detail=f"Failed to save Aadhaar details: {str(exc)}")
