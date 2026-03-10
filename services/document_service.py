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
from db.database_repository import (
    create_pan,
    create_aadhaar,
    create_passport,
    create_driving_license,
    create_voter_id,
    create_handwritten_text_ocr,
    create_digital_text_ocr,
    create_miscellaneous_text_ocr,
    retrieve_all_handwritten_text_ocr,
    retrieve_all_digital_text_ocr,
    retrieve_all_miscellaneous_text_ocr,
)


def process_pan(db: Session, data: dict):
    pan = PanCreate(**data)
    return create_pan(db, pan)


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