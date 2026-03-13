import json
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from llm.inference import call_vision_model
from prompts.account_opening.page1_schema import PAGE1_PROMPT
from services.file_service import convert_image_to_base64
from schemas.account_opening_schemas import AccountFormCreate, AccountFormPageCreate
from db.repositories.account_opening_repository import create_account_form, create_account_form_page
import logging
logger = logging.getLogger(__name__)

async def extract_account_opening_page1(file: UploadFile, db: Session):
    """
    Extract data from Account Opening Form Page 1.
    Creates entries in both account_forms and account_form_pages tables.
    """
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
    response = call_vision_model(
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
    db_form = create_account_form(
        db=db,
        account_form=account_form_data,
        created_by="system"
    )

    # -------------------------------
    # Create Account Form Page Entry
    # -------------------------------
    page_data_json = json.dumps(response, indent=2)
    
    form_page_data = AccountFormPageCreate(
        form_id=str(db_form.id),
        page_number=1,
        page_data=page_data_json,
        created_by="system"
    )

    # Save page data to database
    db_page = create_account_form_page(
        db=db,
        form_page=form_page_data,
        created_by="system"
    )

    # -------------------------------
    # Return response
    # -------------------------------
    return {
        "status": "success",
        "form_id": db_form.id,
        "page_number": db_page.page_number,
        "page1_data": response,
        "message": "Account opening form page 1 processed and saved successfully"
    }