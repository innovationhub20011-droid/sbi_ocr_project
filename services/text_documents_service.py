import base64
import logging

from fastapi import HTTPException, UploadFile

from llm.inference import call_vision_model_raw_async
from services.text_services import save_text_document_ocr
from services.file_service import convert_pdf_to_images
from utils.text_document_utils import clean_ocr_text, pil_image_to_base64

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES = (".png", ".jpg", ".jpeg")


async def _extract_pages_from_upload(file: UploadFile) -> list[str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    lower_name = file.filename.lower()

    if lower_name.endswith(".pdf"):
        pdf_images = await convert_pdf_to_images(file)
        return [pil_image_to_base64(img) for img in pdf_images]

    if lower_name.endswith(SUPPORTED_IMAGE_TYPES):
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        return [base64.b64encode(content).decode("utf-8")]

    raise HTTPException(
        status_code=400,
        detail="Only PDF, PNG, JPG, JPEG files are allowed"
    )


async def extract_text_document(file: UploadFile, document_type: str, prompt: str) -> dict:
    file_name = file.filename or "unknown_file"
    page_images_base64 = await _extract_pages_from_upload(file)
    total_pages = len(page_images_base64)
    pages = []

    try:
        for idx, image_base64 in enumerate(page_images_base64, start=1):
            extracted_text = await call_vision_model_raw_async(
                prompt,
                image_base64,
                api_endpoint=f"/extract/text/{document_type}",
                file_name=file_name,
            )
            extracted_text = extracted_text.strip()
            extracted_text = clean_ocr_text(extracted_text)

            pages.append({
                "page_number": idx,
                "extracted_text": extracted_text,
            })

        ocr_result = {"pages": pages}
        save_text_document_ocr(
            {
                "document_type": document_type,
                "file_name": file_name,
                "ocr_result": ocr_result,
                "total_pages": total_pages,
            }
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Text document extraction failed")
        raise HTTPException(status_code=500, detail=f"Text document extraction failed: {str(exc)}")

    return {
        "document_type": document_type,
        "file_name": file_name,
        "total_pages": total_pages,
        "pages": pages,
    }
