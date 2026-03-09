import base64
import logging

from fastapi import UploadFile, HTTPException
from db.database import SessionLocal
from models.document_model import PanCardDetails
from services.document_service import process_pan, retrieve_pan_details
from utils.vision_utils import call_vision_model
from prompts.pan_prompt import PAN_PROMPT
from sqlalchemy.orm import Session
from db.database import SessionLocal


logger = logging.getLogger(__name__)


def empty_pan():
    return {
        "full_name": "",
        "pan_number": "",
        "date_of_birth": "",
        "father_name": ""
    }


async def extract_pan(file: UploadFile) -> dict:

    # -----------------------------
    # 1️⃣ Basic File Validation
    # -----------------------------
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, JPEG images are allowed"
        )

    try:
        # -----------------------------
        # 2️⃣ Read File
        # -----------------------------
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        image_base64 = base64.b64encode(contents).decode("utf-8")

        # -----------------------------
        # 3️⃣ Call Vision Model
        # -----------------------------
        pan_data = call_vision_model(
            PAN_PROMPT,
            image_base64,
            empty_pan()
        )

        # -----------------------------
        # 4️⃣ Save to Database (Non-blocking)
        # -----------------------------
        if pan_data.get("pan_number"):
            db: Session = SessionLocal()
            try:
                process_pan(db, pan_data)
                db.commit()
                
            except HTTPException:
                db.rollback()
                raise  # Propagate business errors (e.g. duplicate Aadhaar)
            
            except Exception:
                db.rollback()
                logger.exception("Failed to save PAN details")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save PAN details"
                )

            finally:
                db.close()

        # -----------------------------
        # 5️⃣ Return Extracted Data
        # -----------------------------
        return {
            "pan_data": pan_data
        }

    except HTTPException:
        raise  # propagate validation errors

    except Exception as exc:
        logger.exception("PAN extraction failed")
        raise HTTPException(
            status_code=500,
            detail=f"PAN extraction failed: {str(exc)}"
        )
        
def get_all_pan():
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