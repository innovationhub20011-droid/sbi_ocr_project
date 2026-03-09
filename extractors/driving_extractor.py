from fastapi import UploadFile, HTTPException
from utils.vision_utils import call_vision_model
from prompts.driving_license_prompt import DRIVING_LICENSE_PROMPT
import base64


def empty_driving_license():
    return {
        "driving_licence_number": "",
        "name": "",
        "father_name": "",
        "date_of_birth": "",
        "date_of_issue": "",
        "valid_till_nt": "",
        "valid_till_tr": "",
        "address": "",
        "blood_group": "",
        "class_of_vehicle": "",
        "issuing_authority": ""
    }


async def extract_driving_license(file: UploadFile) -> dict:

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

        dl_data = call_vision_model(
            DRIVING_LICENSE_PROMPT,
            image_base64,
            empty_driving_license()
        )

        return {
            "driving_license_data": dl_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Driving License extraction failed: {str(e)}"
        )