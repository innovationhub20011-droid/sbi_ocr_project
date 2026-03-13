import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.document_model import DrivingLicenseDetails
from schemas.document_schemas import DrivingLicenseCreate

logger = logging.getLogger(__name__)


def create_driving_license(
    db: Session,
    driving_license: DrivingLicenseCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system",
):
    dl_number = (driving_license.driving_licence_number or "").strip() or None

    if dl_number:
        existing = db.query(DrivingLicenseDetails).filter(
            DrivingLicenseDetails.driving_licence_number == dl_number
        ).first()
        if existing:
            logger.warning("Driving License %s already exists in database.", dl_number)
            raise HTTPException(status_code=400, detail="Data for this driving license already exists in the database.")

    db_dl = DrivingLicenseDetails(
        driving_licence_number=dl_number,
        name=driving_license.name,
        father_name=driving_license.father_name,
        date_of_birth=driving_license.date_of_birth,
        date_of_issue=driving_license.date_of_issue,
        valid_till_nt=driving_license.valid_till_nt,
        valid_till_tr=driving_license.valid_till_tr,
        address=driving_license.address,
        blood_group=driving_license.blood_group,
        class_of_vehicle=driving_license.class_of_vehicle,
        issuing_authority=driving_license.issuing_authority,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_dl)
        db.commit()
        db.refresh(db_dl)
        return db_dl
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data for this driving license already exists in the database.")
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving driving license")
        raise HTTPException(status_code=500, detail=f"Failed to save driving license details: {str(exc)}")
