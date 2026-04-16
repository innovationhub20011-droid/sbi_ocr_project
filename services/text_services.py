import json

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from db.database import SessionLocal
from models.document_model import DigitalTextOcrDetails, HandwrittenTextOcrDetails, MiscellaneousTextOcrDetails
from schemas.document_schemas import TextDocumentOcrCreate


def _serialize_record(record) -> dict:
    return {key: value for key, value in record.__dict__.items() if not key.startswith("_")}


def _open_session():
    return SessionLocal()


def save_text_document_ocr(data: dict):
    ocr_data = TextDocumentOcrCreate(**data)
    db = _open_session()
    try:
        model_map = {
            "handwritten_text": (HandwrittenTextOcrDetails, "Handwritten Text Document"),
            "digital_text": (DigitalTextOcrDetails, "Digital Text Document"),
            "miscellaneous_text": (MiscellaneousTextOcrDetails, "Miscellaneous Text Documents"),
        }
        model_cls, label = model_map[ocr_data.document_type]

        db_record = model_cls(
            document_type=label,
            file_name=ocr_data.file_name,
            ocr_result=json.dumps(ocr_data.ocr_result, ensure_ascii=True),
            total_pages=ocr_data.total_pages,
            ocr_source=ocr_data.ocr_source,
            created_by="system",
        )

        try:
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            return {"record": db_record, "saved": True, "warning": None}
        except IntegrityError:
            db.rollback()
            return {"record": db_record, "saved": False, "warning": "Data already exists in the database."}
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save text document OCR: {str(exc)}")
    finally:
        db.close()


def retrieve_handwritten_text_details() -> list[dict]:
    db = _open_session()
    try:
        records = db.query(HandwrittenTextOcrDetails).order_by(HandwrittenTextOcrDetails.id.desc()).all()
        return [_serialize_record(record) | {"ocr_result": json.loads(record.ocr_result) if record.ocr_result else {}} for record in records]
    finally:
        db.close()


def retrieve_digital_text_details() -> list[dict]:
    db = _open_session()
    try:
        records = db.query(DigitalTextOcrDetails).order_by(DigitalTextOcrDetails.id.desc()).all()
        return [_serialize_record(record) | {"ocr_result": json.loads(record.ocr_result) if record.ocr_result else {}} for record in records]
    finally:
        db.close()


def retrieve_miscellaneous_text_details() -> list[dict]:
    db = _open_session()
    try:
        records = db.query(MiscellaneousTextOcrDetails).order_by(MiscellaneousTextOcrDetails.id.desc()).all()
        return [_serialize_record(record) | {"ocr_result": json.loads(record.ocr_result) if record.ocr_result else {}} for record in records]
    finally:
        db.close()
