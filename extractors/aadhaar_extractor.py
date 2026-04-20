import asyncio
import base64
import logging
from typing import Any

from fastapi import HTTPException, UploadFile

from llm.inference import call_vision_model_async
from prompts.aadhaar_prompt import AADHAAR_PROMPT
from services.ovd_services import save_aadhaar_details
from utils.document_classifier import validate_document_type
from utils.face_detection import detect_first_face, face_to_data_url

logger = logging.getLogger(__name__)


def empty_aadhaar() -> dict:
    return {
        "full_name": "",
        "date_of_birth": "",
        "gender": "",
        "aadhaar_number": "",
        "address": "",
    }


async def extract_aadhaar(file: UploadFile, photo: bool = False) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG images are allowed")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            is_valid, predicted_label, confidence = validate_document_type(contents, "aadhaar")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Uploaded document was not an Aadhaar card"
                ),
            )

        image_base64 = base64.b64encode(contents).decode("utf-8")
        vision_task = call_vision_model_async(
            AADHAAR_PROMPT,
            image_base64,
            empty_aadhaar(),
            api_endpoint="/extract/aadhaar",
            file_name=file.filename,
        )
        face_task = asyncio.to_thread(detect_first_face, image_base64) if photo else None

        if face_task is None:
            aadhaar_data = await vision_task
            face_crop = None
        else:
            aadhaar_data, face_crop = await asyncio.gather(vision_task, face_task)

        response: dict[str, Any] = {"aadhaar_data": aadhaar_data}

        if aadhaar_data.get("aadhaar_number"):
            aadhaar_result = save_aadhaar_details(aadhaar_data)
            if aadhaar_result.get("warning"):
                response["warning"] = aadhaar_result["warning"]

        if photo:
            response["face_image"] = face_to_data_url(face_crop) if face_crop is not None else None

        return response

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Aadhaar extraction failed")
        raise HTTPException(status_code=500, detail=f"Aadhaar extraction failed: {str(exc)}")
