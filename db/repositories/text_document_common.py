import json
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def save_text_document_ocr(db: Session, ocr_data, model_cls, document_type_label: str, created_by: str = "system"):
    db_record = model_cls(
        document_type=document_type_label,
        file_name=ocr_data.file_name,
        ocr_result=json.dumps(ocr_data.ocr_result, ensure_ascii=True),
        total_pages=ocr_data.total_pages,
        ocr_source=ocr_data.ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_record)
        db.flush()
        return db_record
    except Exception as exc:
        logger.exception("Unexpected error while saving text document OCR")
        raise HTTPException(status_code=500, detail=f"Failed to save text document OCR: {str(exc)}")


def serialize_ocr_records(records):
    serialized = []
    for record in records:
        item = {
            "id": record.id,
            "document_type": record.document_type,
            "file_name": record.file_name,
            "ocr_result": json.loads(record.ocr_result) if record.ocr_result else {},
            "total_pages": record.total_pages,
            "ocr_source": record.ocr_source,
            "is_verified": record.is_verified,
            "verified_by": record.verified_by,
            "verified_date": record.verified_date,
            "created_by": record.created_by,
            "created_date": record.created_date,
            "updated_by": record.updated_by,
            "updated_date": record.updated_date,
        }
        serialized.append(item)
    return serialized
