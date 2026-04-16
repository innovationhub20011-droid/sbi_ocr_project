from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.document_model import AadhaarCardDetails, PanCardDetails
from schemas.document_schemas import (
    PanCreate,
    AadhaarCreate,
    PassportCreate,
    DrivingLicenseCreate,
    VoterIdCreate,
    TextDocumentOcrCreate,
)
from db.repositories.aadhaar_repository import create_aadhaar
from db.repositories.passport_repository import create_passport
from db.repositories.driving_license_repository import create_driving_license
from db.repositories.voter_id_repository import create_voter_id
from db.repositories.handwritten_text_repository import (
    create_handwritten_text_ocr,
    retrieve_all_handwritten_text_ocr,
)
from db.repositories.digital_text_repository import (
    create_digital_text_ocr,
    retrieve_all_digital_text_ocr,
)
from db.repositories.miscellaneous_text_repository import (
    create_miscellaneous_text_ocr,
    retrieve_all_miscellaneous_text_ocr,
)


def _extract_pan_value(field):
    if isinstance(field, dict):
        value = field.get("value", "")
        return value if value is not None else ""
    return field if field is not None else ""


def normalize_pan_data(data: dict) -> dict:
    return {
        "pan_number": _extract_pan_value(data.get("pan_number")),
        "full_name": _extract_pan_value(data.get("full_name")),
        "father_name": _extract_pan_value(data.get("father_name")),
        "date_of_birth": _extract_pan_value(data.get("date_of_birth")),
    }


def process_pan(db: Session, data: dict):
    pan = PanCreate(**normalize_pan_data(data))

    existing = db.query(PanCardDetails).filter(
        PanCardDetails.pan_number == pan.pan_number
    ).first()

    if existing:
        return {
            "record": existing,
            "saved": False,
            "warning": "Data for this PAN card already exists in the database.",
        }

    db_pan = PanCardDetails(
        pan_number=pan.pan_number,
        full_name=pan.full_name,
        father_name=pan.father_name,
        date_of_birth=pan.date_of_birth,
        pan_type=pan.derive_pan_type(),
        ocr_source="vision_model",
        created_by="system",
    )

    try:
        db.add(db_pan)
        db.commit()
        db.refresh(db_pan)
        return {"record": db_pan, "saved": True, "warning": None}
    except IntegrityError:
        db.rollback()
        existing = db.query(PanCardDetails).filter(
            PanCardDetails.pan_number == pan.pan_number
        ).first()
        return {
            "record": existing,
            "saved": False,
            "warning": "Data for this PAN card already exists in the database.",
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save PAN details: {str(exc)}")


def process_aadhaar(db: Session, data: dict):
    aadhaar = AadhaarCreate(**data)
    return create_aadhaar(db, aadhaar)


def process_passport(db: Session, data: dict):
    passport = PassportCreate(**data)
    return create_passport(db, passport)


def process_driving_license(db: Session, data: dict):
    dl_data = DrivingLicenseCreate(**data)
    return create_driving_license(db, dl_data)


def process_voter_id(db: Session, data: dict):
    voter_data = VoterIdCreate(**data)
    return create_voter_id(db, voter_data)

def process_text_document_ocr(db: Session, data: dict):
    ocr_data = TextDocumentOcrCreate(**data)
    if ocr_data.document_type == "handwritten_text":
        return create_handwritten_text_ocr(db, ocr_data)
    if ocr_data.document_type == "digital_text":
        return create_digital_text_ocr(db, ocr_data)
    if ocr_data.document_type == "miscellaneous_text":
        return create_miscellaneous_text_ocr(db, ocr_data)
    raise ValueError("Unsupported text document type")


def retrieve_handwritten_text_details(db: Session):
    return retrieve_all_handwritten_text_ocr(db)


def retrieve_digital_text_details(db: Session):
    return retrieve_all_digital_text_ocr(db)


def retrieve_miscellaneous_text_details(db: Session):
    return retrieve_all_miscellaneous_text_ocr(db)

def retrieve_pan_details(db: Session):
    return db.query(PanCardDetails).all()

def retrieve_aadhaar_details(db: Session):
    return db.query(AadhaarCardDetails).all()
