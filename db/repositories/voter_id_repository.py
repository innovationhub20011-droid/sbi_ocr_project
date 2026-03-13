import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.document_model import VoterIdDetails
from schemas.document_schemas import VoterIdCreate

logger = logging.getLogger(__name__)


def create_voter_id(
    db: Session,
    voter_id: VoterIdCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system",
):
    epic_number = (voter_id.epic_number or "").strip() or None

    if epic_number:
        existing = db.query(VoterIdDetails).filter(
            VoterIdDetails.epic_number == epic_number
        ).first()
        if existing:
            logger.warning("Voter EPIC %s already exists in database.", epic_number)
            raise HTTPException(status_code=400, detail="Data for this voter ID already exists in the database.")

    db_voter = VoterIdDetails(
        epic_number=epic_number,
        name=voter_id.name,
        father_name=voter_id.father_name,
        gender=voter_id.gender,
        date_of_birth=voter_id.date_of_birth,
        address=voter_id.address,
        electoral_registration_officer=voter_id.electoral_registration_officer,
        assembly_constituency=voter_id.assembly_constituency,
        download_date=voter_id.download_date,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_voter)
        db.commit()
        db.refresh(db_voter)
        return db_voter
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data for this voter ID already exists in the database.")
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving voter ID")
        raise HTTPException(status_code=500, detail=f"Failed to save voter ID details: {str(exc)}")
