from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from utils.vision_utils import call_vision_model
from prompts.passport_prompt import PASSPORT_PROMPT
from services.file_service import convert_image_to_base64
from services.document_service import process_passport


def empty_passport():
    return {
        "passport_number": "",
        "surname": "",
        "given_names": "",
        "nationality": "",
        "sex": "",
        "date_of_birth": "",
        "place_of_birth": "",
        "date_of_issue": "",
        "date_of_expiry": "",
        "place_of_issue": "",
        "father_name": "",
        "mother_name": "",
        "address": "",
        "pin_code": "",
        "file_number": ""
    }


async def extract_passport(file: UploadFile):

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    image_base64 = await convert_image_to_base64(file)

    response = call_vision_model(
        PASSPORT_PROMPT,
        image_base64,
        empty_passport()
    )

    # Optional: Validate formats

    import re

    # Passport number (Indian format)
    if not re.match(r"^[A-Z][0-9]{7}$", response.get("passport_number", "")):
        response["passport_number"] = ""

    # PIN code validation
    if not re.match(r"^[0-9]{6}$", response.get("pin_code", "")):
        response["pin_code"] = ""

    db: Session = SessionLocal()
    try:
        process_passport(db, response)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save passport details: {str(exc)}")
    finally:
        db.close()

    return {"passport_data": response}