import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.document_model import PassportDetails
from schemas.document_schemas import PassportCreate

logger = logging.getLogger(__name__)


def create_passport(
    db: Session,
    passport: PassportCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system",
):
    passport_number = (passport.passport_number or "").strip() or None

    if passport_number:
        existing = db.query(PassportDetails).filter(
            PassportDetails.passport_number == passport_number
        ).first()
        if existing:
            logger.warning("Passport %s already exists in database.", passport_number)
            raise HTTPException(status_code=400, detail="Data for this passport already exists in the database.")

    db_passport = PassportDetails(
        passport_number=passport_number,
        surname=passport.surname,
        given_names=passport.given_names,
        nationality=passport.nationality,
        sex=passport.sex,
        date_of_birth=passport.date_of_birth,
        place_of_birth=passport.place_of_birth,
        date_of_issue=passport.date_of_issue,
        date_of_expiry=passport.date_of_expiry,
        place_of_issue=passport.place_of_issue,
        father_name=passport.father_name,
        mother_name=passport.mother_name,
        address=passport.address,
        pin_code=passport.pin_code,
        file_number=passport.file_number,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_passport)
        db.commit()
        db.refresh(db_passport)
        return db_passport
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data for this passport already exists in the database.")
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving passport")
        raise HTTPException(status_code=500, detail=f"Failed to save passport details: {str(exc)}")
