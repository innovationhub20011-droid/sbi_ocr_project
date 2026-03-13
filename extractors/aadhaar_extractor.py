import base64
import logging

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import SessionLocal
from llm.inference import call_vision_model
from prompts.aadhaar_prompt import AADHAAR_PROMPT
from services.document_service import process_aadhaar

logger = logging.getLogger(__name__)


def empty_aadhaar() -> dict:
    return {
        "full_name": "",
        "date_of_birth": "",
        "gender": "",
        "aadhaar_number": "",
        "address": "",
    }


async def extract_aadhaar(file: UploadFile) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG images are allowed")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        image_base64 = base64.b64encode(contents).decode("utf-8")
        aadhaar_data = call_vision_model(
            AADHAAR_PROMPT,
            image_base64,
            empty_aadhaar(),
            api_endpoint="/extract/aadhaar",
            file_name=file.filename,
        )

        if aadhaar_data.get("aadhaar_number"):
            db: Session = SessionLocal()
            try:
                process_aadhaar(db, aadhaar_data)
                db.commit()
            except HTTPException:
                db.rollback()
                raise
            except Exception:
                db.rollback()
                logger.exception("Failed to save Aadhaar details")
                raise HTTPException(status_code=500, detail="Failed to save Aadhaar details")
            finally:
                db.close()

        return {"aadhaar_data": aadhaar_data}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Aadhaar extraction failed")
        raise HTTPException(status_code=500, detail=f"Aadhaar extraction failed: {str(exc)}")
