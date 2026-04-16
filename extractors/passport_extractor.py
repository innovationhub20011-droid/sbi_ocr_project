import logging
import re

from fastapi import UploadFile, HTTPException

from llm.inference import call_vision_model_async
from prompts.passport_prompt import PASSPORT_PROMPT
from services.file_service import convert_image_to_base64
from services.ovd_services import save_passport_details

logger = logging.getLogger(__name__)


def _has_meaningful_content(data: dict) -> bool:
    for value in data.values():
        if isinstance(value, str) and value.strip():
            return True
        if value not in (None, "", {}, [], ()):
            return True
    return False


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
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File must have a name")

        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(status_code=400, detail="Only image files allowed")

        image_base64 = await convert_image_to_base64(file)

        response = await call_vision_model_async(
            PASSPORT_PROMPT,
            image_base64,
            empty_passport(),
            api_endpoint="/extract/passport",
            file_name=file.filename,
        )

        # Passport number (Indian format)
        if not re.match(r"^[A-Z][0-9]{7}$", response.get("passport_number", "")):
            response["passport_number"] = ""

        # PIN code validation
        if not re.match(r"^[0-9]{6}$", response.get("pin_code", "")):
            response["pin_code"] = ""

        if _has_meaningful_content(response):
            save_passport_details(response)
        else:
            logger.info("Skipping passport save because extraction returned no meaningful content")

        return {"passport_data": response}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Passport extraction failed")
        raise HTTPException(status_code=500, detail=f"Passport extraction failed: {str(exc)}")
