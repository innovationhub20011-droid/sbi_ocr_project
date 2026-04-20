import asyncio
import base64
import logging
from typing import Any

from fastapi import HTTPException, UploadFile

from llm.inference import call_vision_model_async
from prompts.pan_prompt import PAN_PROMPT
from services.ovd_services import save_pan_details
from utils.document_classifier import validate_document_type
from utils.face_detection import detect_first_face, face_to_data_url
from utils.signature_detection import detect_first_signature, signature_to_data_url

logger = logging.getLogger(__name__)


def empty_pan() -> dict:
    return {
        "full_name": "",
        "pan_number": "",
        "date_of_birth": "",
        "father_name": "",
    }


async def extract_pan(file: UploadFile, photo: bool = False, signature: bool = False) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG images are allowed")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            is_valid, predicted_label, confidence = validate_document_type(contents, "pan")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Uploaded document is not a PAN card "
                ),
            )

        image_base64 = base64.b64encode(contents).decode("utf-8")
        vision_task = call_vision_model_async(
            PAN_PROMPT,
            image_base64,
            empty_pan(),
            "/extract/pan",
            file.filename,
        )
        signature_task = asyncio.to_thread(detect_first_signature, image_base64) if signature else None
        face_task = asyncio.to_thread(detect_first_face, image_base64) if photo else None

        signature_crop = None
        face_crop = None

        if signature_task is not None and face_task is not None:
            pan_data, signature_crop, face_crop = await asyncio.gather(vision_task, signature_task, face_task)
        elif signature_task is not None:
            pan_data, signature_crop = await asyncio.gather(vision_task, signature_task)
        elif face_task is not None:
            pan_data, face_crop = await asyncio.gather(vision_task, face_task)
        else:
            pan_data = await vision_task

        response: dict[str, Any] = {"pan_data": pan_data}

        try:
            pan_result = save_pan_details(pan_data)
            if pan_result.get("warning"):
                response["warning"] = pan_result["warning"]
        except HTTPException:
            raise
        except Exception:
            logger.exception("Failed to process PAN details")
            raise HTTPException(status_code=500, detail="Failed to save PAN details")

        if signature_task is not None:
            response["signature_image"] = (
                signature_to_data_url(signature_crop) if signature_crop is not None else None
            )

        if face_task is not None:
            response["face_image"] = face_to_data_url(face_crop) if face_crop is not None else None

        return response

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("PAN extraction failed")
        raise HTTPException(status_code=500, detail=f"PAN extraction failed: {str(exc)}")
