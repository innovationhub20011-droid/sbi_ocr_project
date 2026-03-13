import base64
import logging

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import SessionLocal
from llm.inference import call_vision_model
from prompts.pan_prompt import PAN_PROMPT
from services.document_service import process_pan

logger = logging.getLogger(__name__)


def empty_pan() -> dict:
    return {
        "full_name": "",
        "pan_number": "",
        "date_of_birth": "",
        "father_name": "",
    }


async def extract_pan(file: UploadFile) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG images are allowed")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        image_base64 = base64.b64encode(contents).decode("utf-8")
        pan_data = call_vision_model(
            PAN_PROMPT,
            image_base64,
            empty_pan(),
            api_endpoint="/extract/pan",
            file_name=file.filename,
        )

        if pan_data.get("pan_number"):
            db: Session = SessionLocal()
            try:
                process_pan(db, pan_data)
                db.commit()
            except HTTPException:
                db.rollback()
                raise
            except Exception:
                db.rollback()
                logger.exception("Failed to save PAN details")
                raise HTTPException(status_code=500, detail="Failed to save PAN details")
            finally:
                db.close()

        return {"pan_data": pan_data}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("PAN extraction failed")
        raise HTTPException(status_code=500, detail=f"PAN extraction failed: {str(exc)}")
