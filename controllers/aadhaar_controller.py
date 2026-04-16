import logging

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import SessionLocal
from extractors.aadhaar_extractor import extract_aadhaar as _extract_aadhaar
from services.document_service import retrieve_aadhaar_details

logger = logging.getLogger(__name__)


def _serialize_record(record) -> dict:
    return {key: value for key, value in record.__dict__.items() if not key.startswith("_")}


async def extract_aadhaar(file: UploadFile) -> dict:
    """Controller wrapper to keep route layer consistent across document types."""
    return await _extract_aadhaar(file)


def get_all_aadhaar() -> list[dict]:
    db: Session = SessionLocal()
    try:
        aadhaar_records = retrieve_aadhaar_details(db)

        return [_serialize_record(record) for record in aadhaar_records]

    except Exception as exc:
        logger.exception("Failed to retrieve Aadhaar records")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve Aadhaar records: {str(exc)}"
        )
    finally:
        db.close()
