import logging

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import SessionLocal
from extractors.pan_extractor import extract_pan as _extract_pan
from services.document_service import retrieve_pan_details


logger = logging.getLogger(__name__)


async def extract_pan(file: UploadFile) -> dict:
    """Controller wrapper to keep route layer consistent across document types."""
    return await _extract_pan(file)


def get_all_pan() -> dict:
    db: Session = SessionLocal()
    try:
        pan_records = retrieve_pan_details(db)
        return {"pan_cards": [record.__dict__ for record in pan_records]}

    except Exception as exc:
        logger.exception("Failed to retrieve PAN records")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve PAN records: {str(exc)}"
        )

    finally:
        db.close()