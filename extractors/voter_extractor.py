from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from llm.inference import call_vision_model
from prompts.voter_prompt import VOTER_ID_PROMPT
from services.document_service import process_voter_id
import base64


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

        voter_data = call_vision_model(
            VOTER_ID_PROMPT,
            image_base64,
            empty_voter_id(),
            api_endpoint="/extract/voter-id",
            file_name=file.filename,
        )

        db: Session = SessionLocal()
        try:
            process_voter_id(db, voter_data)
            db.commit()
        except HTTPException:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save voter ID details: {str(exc)}")
        finally:
            db.close()

        return {
            "voter_id_data": voter_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voter ID extraction failed: {str(e)}"
        )