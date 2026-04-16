import logging

from fastapi import HTTPException, UploadFile

from extractors.pan_extractor import extract_pan as _extract_pan
from services.ovd_services import retrieve_pan_details


logger = logging.getLogger(__name__)

async def extract_pan(file: UploadFile, photo: bool = False) -> dict:
    """Controller wrapper to keep route layer consistent across document types."""
    return await _extract_pan(file, photo=photo)


def get_all_pan() -> dict:
    try:
        pan_records = retrieve_pan_details()
        return {"pan_cards": pan_records}

    except Exception as exc:
        logger.exception("Failed to retrieve PAN records")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve PAN records: {str(exc)}"
        )
