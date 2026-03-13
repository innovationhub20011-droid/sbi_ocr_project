from fastapi import UploadFile, HTTPException
from prompts.account_opening.page2_schema import PAGE2_PROMPT
from llm.inference import call_vision_model
from services.file_service import convert_image_to_base64


def empty_page2():
    return {
  "proof_of_identity": {
    "document_type": "",
    "equivalent_edocument": "",
    "document_number": "",
    "issued_by": "",
    "issue_date": "",
    "expiry_date": ""
  },
  "foreign_national_details": {
    "visa_details": "",
    "issued_by": "",
    "issue_date": "",
    "expiry_date": ""
  },
  "current_address": {
    "address_type": "",
    "address_line1": "",
    "address_line2": "",
    "city": "",
    "district": "",
    "state": "",
    "pin": "",
    "country": ""
  },
  "correspondence_address": {
    "address_type": "",
    "address_line1": "",
    "address_line2": "",
    "city": "",
    "district": "",
    "state": "",
    "pin": "",
    "country": ""
  },
  "additional_ovd_document": {
    "document_type": "",
    "document_number": "",
    "date": ""
  },
  "declaration": {
    "consent_for_aadhaar_auth": "",
    "place": "",
    "date": ""
  },
  "office_use": {
    "documents_received": "",
    "aadhaar_verification": "",
    "threshold_limit": "",
    "bis_organization_code": "",
    "customer_segment": "",
    "depositor_type": "",
    "risk_category": "",
    "permitted_to_open_cif": "",
    "official_name": "",
    "pf_number": "",
    "ss_number": "",
    "designation": "",
    "office_date": ""
  }}

async def extract_account_opening_page2(file: UploadFile):

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
        prompt=PAGE2_PROMPT,
        image_base64=image_base64,
      empty_schema=empty_page2(),
      api_endpoint="/extract/account-opening/page2",
      file_name=file.filename,
    )

    return {"page2_data": response}