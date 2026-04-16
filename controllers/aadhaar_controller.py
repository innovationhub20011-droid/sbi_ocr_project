import logging

from fastapi import HTTPException, UploadFile

from extractors.aadhaar_extractor import extract_aadhaar as _extract_aadhaar
from services.ovd_services import retrieve_aadhaar_details

logger = logging.getLogger(__name__)

async def extract_aadhaar(file: UploadFile, photo: bool = False) -> dict:
    """Controller wrapper to keep route layer consistent across document types."""
    return await _extract_aadhaar(file, photo=photo)


def get_all_aadhaar() -> list[dict]:
    try:
        return retrieve_aadhaar_details()

    except Exception as exc:
        logger.exception("Failed to retrieve Aadhaar records")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve Aadhaar records: {str(exc)}"
        )
