from fastapi import UploadFile, HTTPException
from utils.vision_utils import call_vision_model
from prompts.account_opening.page1_schema import PAGE1_PROMPT
from services.file_service import convert_image_to_base64

def empty_page1():
    return {
        "top_section": {
            "branch_name": "",
            "branch_code": "",
            "date": "",
            "customer_id": "",
            "account_number": "",
            "account_type": "",
            "ckyc_number": "",
            "pf_number": ""
        },
        "personal_section": {
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "dob": "",
            "gender": "",
            "marital_status": "",
            "parent_or_spouse_name": "",
            "guardian_name": "",
            "relationship_with_guardian": "",
            "nationality": "",
            "citizenship": "",
            "occupation_type": "",
            "employee_id": "",
            "place_of_posting": "",
            "organization_name": "",
            "nature_of_business": "",
            "designation": "",
            "annual_income": "",
            "net_worth": "",
            "source_of_funds": "",
            "religion": "",
            "category": "",
            "person_with_disability": "",
            "education": "",
            "politically_exposed": "",
            "pan_number": ""
        },
        "contact_section": {
            "mobile_number": "",
            "email": "",
            "std_tel_off": "",
            "tel_res": ""
        }
    }


async def extract_account_opening_page1(file: UploadFile):

    # -------------------------------
    # File Validation
    # -------------------------------
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    # -------------------------------
    # Convert to base64
    # -------------------------------
    image_base64 = await convert_image_to_base64(file)

    # -------------------------------
    # Call Vision Model
    # -------------------------------
    response = call_vision_model(
        prompt=PAGE1_PROMPT,
        image_base64=image_base64,
        empty_schema=empty_page1()
    )

    return {"page1_data": response}