from fastapi import UploadFile, HTTPException
from db.database import SessionLocal
from services.document_service import process_raw_text
from utils.vision_utils import call_vision_model_raw
from prompts.generic_ocr_prompt import GENERIC_OCR_PROMPT
import base64
import logging
logger = logging.getLogger(__name__)


async def extract_raw_text(file: UploadFile) -> dict:

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, JPEG images are allowed"
        )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        image_base64 = base64.b64encode(contents).decode("utf-8")
        
        raw_text = call_vision_model_raw(
            GENERIC_OCR_PROMPT,
            image_base64
        )
        if raw_text:
            db = SessionLocal()
            try:
                process_raw_text(db, {"document_text": raw_text})
                db.commit()
                
            except HTTPException:
                db.rollback()
                raise  # Propagate business errors
            
            except Exception:
                db.rollback()
                logger.exception("Failed to save RAW text")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save RAW text"
                )

            finally:
                db.close()

        return {
            "document_text": raw_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR extraction failed: {str(e)}"
        )