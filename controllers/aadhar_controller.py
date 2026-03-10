import base64
import logging

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from models.document_model import AadhaarCardDetails
from services.document_service import process_aadhaar, retrieve_aadhaar_details
from utils.vision_utils import call_vision_model
from prompts.aadhaar_prompt import AADHAAR_PROMPT

logger = logging.getLogger(__name__)


def empty_aadhaar():
    return {
        "full_name": "",
        "date_of_birth": "",
        "gender": "",
        "aadhaar_number": "",
        "address": ""
    }


async def extract_aadhaar(file: UploadFile) -> dict:

    # ---------------------------------
    # 1️⃣ Basic File Validation
    # ---------------------------------
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, JPEG images are allowed"
        )

    try:
        # ---------------------------------
        # 2️⃣ Read File
        # ---------------------------------
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        image_base64 = base64.b64encode(contents).decode("utf-8")

        # ---------------------------------
        # 3️⃣ Call Vision Model
        # ---------------------------------
        aadhaar_data = call_vision_model(
            AADHAAR_PROMPT,
            image_base64,
            empty_aadhaar()
        )

        # ---------------------------------
        # 4️⃣ Save to Database (if Aadhaar detected)
        # ---------------------------------
        if aadhaar_data.get("aadhaar_number"):
            db: Session = SessionLocal()
            try:
                process_aadhaar(db, aadhaar_data)
                db.commit()

            except HTTPException:
                db.rollback()
                raise  # Propagate business errors (e.g. duplicate Aadhaar)

            except Exception:
                db.rollback()
                logger.exception("Failed to save Aadhaar details")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save Aadhaar details"
                )

            finally:
                db.close()

        # ---------------------------------
        # 5️⃣ Return Extracted Data
        # ---------------------------------
        return {
            "aadhaar_data": aadhaar_data
        }

    except HTTPException:
        raise  # propagate validation errors

    except Exception as exc:
        logger.exception("Aadhaar extraction failed")
        raise HTTPException(
            status_code=500,
            detail=f"Aadhaar extraction failed: {str(exc)}"
        )

def get_all_aadhaar():
    db: Session = SessionLocal()
    try:
        aadhaar_records = retrieve_aadhaar_details(db)
        
        return [record.__dict__ for record in aadhaar_records]

    except Exception as exc:
        logger.exception("Failed to retrieve Aadhaar records")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve Aadhaar records: {str(exc)}"
        )
    finally:
        db.close()