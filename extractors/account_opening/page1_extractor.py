from fastapi import UploadFile, HTTPException
from utils.vision_utils import call_vision_model
from prompts.account_opening.page1_schema import PAGE1_PROMPT
from services.file_service import convert_image_to_base64


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
        empty_schema={}
    )

    return {"page1_data": response}