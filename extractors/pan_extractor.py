import asyncio
import base64
import logging
from typing import Any

from fastapi import HTTPException, UploadFile

from db.database import SessionLocal
from llm.inference import call_vision_model
from prompts.pan_prompt import PAN_PROMPT
from services.document_service import process_pan
from utils.face_detection import detect_first_face, face_to_data_url

logger = logging.getLogger(__name__)


def empty_pan() -> dict:
    return {
        "full_name": "",
        "pan_number": "",
        "date_of_birth": "",
        "father_name": "",
    }


async def extract_pan(file: UploadFile, photo: bool = False) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG images are allowed")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        image_base64 = base64.b64encode(contents).decode("utf-8")
        vision_task = asyncio.to_thread(
            call_vision_model,
            PAN_PROMPT,
            image_base64,
            empty_pan(),
            "/extract/pan",
            file.filename,
        )
        face_task = asyncio.to_thread(detect_first_face, image_base64) if photo else None

        if face_task is None:
            pan_data = await vision_task
            face_crop = None
        else:
            pan_data, face_crop = await asyncio.gather(vision_task, face_task)

        response: dict[str, Any] = {"pan_data": pan_data}

        db = SessionLocal()
        try:
            pan_result = process_pan(db, pan_data)
            if pan_result.get("warning"):
                response["warning"] = pan_result["warning"]
        except HTTPException:
            raise
        except Exception:
            logger.exception("Failed to process PAN details")
            raise HTTPException(status_code=500, detail="Failed to save PAN details")
        finally:
            db.close()

        if photo:
            response["face_image"] = face_to_data_url(face_crop) if face_crop is not None else None

        return response

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("PAN extraction failed")
        raise HTTPException(status_code=500, detail=f"PAN extraction failed: {str(exc)}")
