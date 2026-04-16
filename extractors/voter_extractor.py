import base64
import logging

from fastapi import UploadFile, HTTPException

from llm.inference import call_vision_model_async
from prompts.voter_prompt import VOTER_ID_PROMPT
from services.ovd_services import save_voter_id_details

logger = logging.getLogger(__name__)


def _has_meaningful_content(data: dict) -> bool:
    for value in data.values():
        if isinstance(value, str) and value.strip():
            return True
        if value not in (None, "", {}, [], ()):
            return True
    return False


def empty_voter_id():
    return {
        "epic_number": "",
        "name": "",
        "father_name": "",
        "gender": "",
        "date_of_birth": "",
        "address": "",
        "electoral_registration_officer": "",
        "assembly_constituency": "",
        "download_date": ""
    }


async def extract_voter_id(file: UploadFile) -> dict:
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File must have a name")

        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(
                status_code=400,
                detail="Only PNG, JPG, JPEG images are allowed"
            )

        contents = await file.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        image_base64 = base64.b64encode(contents).decode("utf-8")

        voter_data = await call_vision_model_async(
            VOTER_ID_PROMPT,
            image_base64,
            empty_voter_id(),
            api_endpoint="/extract/voter-id",
            file_name=file.filename,
        )

        if _has_meaningful_content(voter_data):
            save_voter_id_details(voter_data)
        else:
            logger.info("Skipping voter ID save because extraction returned no meaningful content")

        return {
            "voter_id_data": voter_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Voter ID extraction failed")
        raise HTTPException(
            status_code=500,
            detail=f"Voter ID extraction failed: {str(e)}"
        )
