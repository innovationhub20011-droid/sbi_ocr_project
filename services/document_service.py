from sqlalchemy.orm import Session
from models.document_model import AadhaarCardDetails, PanCardDetails
from schemas.document_schemas import PanCreate, AadhaarCreate, RawTextCreate
from db.database_repository import create_pan, create_aadhaar, create_raw_text


def process_pan(db: Session, data: dict):
    pan = PanCreate(**data)
    return create_pan(db, pan)


def process_aadhaar(db: Session, data: dict):
    aadhaar = AadhaarCreate(**data)
    return create_aadhaar(db, aadhaar)

def process_raw_text(db: Session, data: dict):
    raw_text = RawTextCreate(**data)
    return create_raw_text(db, raw_text)

def retrieve_pan_details(db: Session):
    return db.query(PanCardDetails).all()

def retrieve_aadhaar_details(db: Session):
    return db.query(AadhaarCardDetails).all()