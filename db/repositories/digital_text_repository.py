from sqlalchemy.orm import Session

from models.document_model import DigitalTextOcrDetails
from schemas.document_schemas import TextDocumentOcrCreate
from db.repositories.text_document_common import save_text_document_ocr, serialize_ocr_records


def create_digital_text_ocr(db: Session, ocr_data: TextDocumentOcrCreate, created_by: str = "system"):
    return save_text_document_ocr(
        db,
        ocr_data,
        DigitalTextOcrDetails,
        "Digital Text Document",
        created_by,
    )


def retrieve_all_digital_text_ocr(db: Session):
    records = db.query(DigitalTextOcrDetails).order_by(DigitalTextOcrDetails.id.desc()).all()
    return serialize_ocr_records(records)
