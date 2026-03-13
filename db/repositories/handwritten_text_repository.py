from sqlalchemy.orm import Session

from models.document_model import HandwrittenTextOcrDetails
from schemas.document_schemas import TextDocumentOcrCreate
from db.repositories.text_document_common import save_text_document_ocr, serialize_ocr_records


def create_handwritten_text_ocr(db: Session, ocr_data: TextDocumentOcrCreate, created_by: str = "system"):
    return save_text_document_ocr(
        db,
        ocr_data,
        HandwrittenTextOcrDetails,
        "Handwritten Text Document",
        created_by,
    )


def retrieve_all_handwritten_text_ocr(db: Session):
    records = db.query(HandwrittenTextOcrDetails).order_by(HandwrittenTextOcrDetails.id.desc()).all()
    return serialize_ocr_records(records)
