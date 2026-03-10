import base64
import logging
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image

from db.database import SessionLocal
from prompts.digital_text_prompt import DIGITAL_TEXT_PROMPT
from prompts.handwritten_text_prompt import HANDWRITTEN_TEXT_PROMPT
from prompts.misc_text_prompt import MISC_TEXT_PROMPT
from services.document_service import (
    process_text_document_ocr,
    retrieve_handwritten_text_details,
    retrieve_digital_text_details,
    retrieve_miscellaneous_text_details,
)
from services.file_service import convert_pdf_to_images
from utils.vision_utils import call_vision_model_raw

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES = (".png", ".jpg", ".jpeg")
SUPPORTED_TEXT_DOC_TYPES = {
    "handwritten_text": HANDWRITTEN_TEXT_PROMPT,
    "digital_text": DIGITAL_TEXT_PROMPT,
    "miscellaneous_text": MISC_TEXT_PROMPT,
}


def _pil_image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


async def _extract_pages_from_upload(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    lower_name = file.filename.lower()

    if lower_name.endswith(".pdf"):
        pdf_images = await convert_pdf_to_images(file)
        return [_pil_image_to_base64(img) for img in pdf_images]

    if lower_name.endswith(SUPPORTED_IMAGE_TYPES):
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        return [base64.b64encode(content).decode("utf-8")]

    raise HTTPException(
        status_code=400,
        detail="Only PDF, PNG, JPG, JPEG files are allowed"
    )


async def extract_text_document(file: UploadFile, document_type: str) -> dict:
    prompt = SUPPORTED_TEXT_DOC_TYPES.get(document_type)
    if not prompt:
        raise HTTPException(status_code=400, detail="Unsupported text document type")

    page_images_base64 = await _extract_pages_from_upload(file)
    total_pages = len(page_images_base64)
    pages = []

    db = SessionLocal()
    try:
        for idx, image_base64 in enumerate(page_images_base64, start=1):
            extracted_text = call_vision_model_raw(prompt, image_base64).strip()

            pages.append(
                {
                    "page_number": idx,
                    "extracted_text": extracted_text,
                }
            )

        ocr_result = {"pages": pages}

        process_text_document_ocr(
            db,
            {
                "document_type": document_type,
                "file_name": file.filename,
                "ocr_result": ocr_result,
                "total_pages": total_pages,
            }
        )

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        logger.exception("Text document extraction failed")
        raise HTTPException(
            status_code=500,
            detail=f"Text document extraction failed: {str(exc)}"
        )

    finally:
        db.close()

    return {
        "document_type": document_type,
        "file_name": file.filename,
        "total_pages": total_pages,
        "pages": pages,
    }


async def extract_handwritten_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "handwritten_text")


async def extract_digital_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "digital_text")


async def extract_misc_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "miscellaneous_text")


def get_all_handwritten_text_ocr() -> dict:
    db = SessionLocal()
    try:
        records = retrieve_handwritten_text_details(db)
        return {"records": records}
    finally:
        db.close()


def get_all_digital_text_ocr() -> dict:
    db = SessionLocal()
    try:
        records = retrieve_digital_text_details(db)
        return {"records": records}
    finally:
        db.close()


def get_all_miscellaneous_text_ocr() -> dict:
    db = SessionLocal()
    try:
        records = retrieve_miscellaneous_text_details(db)
        return {"records": records}
    finally:
        db.close()
