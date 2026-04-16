import json
from fastapi import UploadFile, HTTPException
from llm.inference import call_vision_model_async
from prompts.account_opening.page1_schema import PAGE1_PROMPT
from services.file_service import convert_image_to_base64
from schemas.account_opening_schemas import AccountFormCreate
from services.account_opening_services import save_account_opening_page1
import logging
logger = logging.getLogger(__name__)

async def extract_account_opening_page1(file: UploadFile):
    """
    Extract data from Account Opening Form Page 1.
    Creates entries in both account_forms and account_form_pages tables.
    """
    try:
        logger.info(f"Starting extraction for account opening page 1: {file.filename}")
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
        response = await call_vision_model_async(
            prompt=PAGE1_PROMPT,
            image_base64=image_base64,
            empty_schema={},
            api_endpoint="/extract/account-opening/page1",
            file_name=file.filename,
        )
        logger.info(f"Vision model response for account opening page 1: {response}")

        # Check if extraction failed
        if not response or response == {}:
            logger.error("Vision model returned empty response")
            raise HTTPException(
                status_code=422,
                detail="Extraction failed: Unable to extract data from the image"
            )

        # -------------------------------
        # Extract main form fields
        # -------------------------------
        top_section = response.get("top_section", {})
        personal_section = response.get("personal_section", {})
        contact_section = response.get("contact_section", {})

        # Construct customer name
        first_name = personal_section.get("first_name", "")
        middle_name = personal_section.get("middle_name", "")
        last_name = personal_section.get("last_name", "")
        customer_name = " ".join([first_name, middle_name, last_name]).strip()

        # -------------------------------
        # Create Account Form Entry
        # -------------------------------
        account_form_data = AccountFormCreate(
            branch_code=top_section.get("branch_code") or None,
            account_number=top_section.get("account_number") or None,
            customer_name=customer_name or None,
            pan_number=personal_section.get("pan_number") or None,
            mobile_number=contact_section.get("mobile_number") or None,
            form_status="OCR_COMPLETED",
            created_by="system"
        )

        # Save account form to database
        page_data_json = json.dumps(response, indent=2)
        save_result = save_account_opening_page1(
            form_data=account_form_data,
            page_number=1,
            page_data=page_data_json,
        )

        return {
            "status": save_result["status"],
            "form_id": save_result["form_id"],
            "page_number": save_result["page_number"],
            "page1_data": response,
            "message": "Account opening form page 1 processed and saved successfully"
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Account opening page 1 extraction failed")
        raise HTTPException(status_code=500, detail=f"Account opening page 1 extraction failed: {str(exc)}")
