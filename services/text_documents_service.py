import base64
import logging
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image

from db.database import SessionLocal
from llm.inference import call_vision_model_raw
from services.document_service import process_text_document_ocr
from services.file_service import convert_pdf_to_images

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES = (".png", ".jpg", ".jpeg")


def _pil_image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _clean_ocr_text(raw_text: str) -> str:
    """Collapse model repetition loops while preserving normal paragraph flow."""
    if not raw_text:
        return ""

    cleaned_lines = []
    prev_non_empty = None
    consecutive_repeat_count = 0
    repetitive_short_line_streak = 0
    repeated_dot_streak = 0
    saw_blank = False

    for line in raw_text.splitlines():
        current = line.strip()

        if not current:
            saw_blank = True
            continue

        normalized = current.lower()

        if normalized in {"...", ". . ."}:
            repeated_dot_streak += 1
            if repeated_dot_streak >= 2:
                break
        else:
            repeated_dot_streak = 0

        if normalized == prev_non_empty:
            consecutive_repeat_count += 1
        else:
            consecutive_repeat_count = 0

        if consecutive_repeat_count > 0:
            continue

        token_count = len(current.split())
        if token_count <= 2 and len(current) <= 6:
            repetitive_short_line_streak += 1
        else:
            repetitive_short_line_streak = 0

        if repetitive_short_line_streak >= 8:
            break

        if saw_blank and cleaned_lines:
            cleaned_lines.append("")

        cleaned_lines.append(current)
        prev_non_empty = normalized
        saw_blank = False

    return "\n".join(cleaned_lines).strip()


async def _extract_pages_from_upload(file: UploadFile) -> list[str]:
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


async def extract_text_document(file: UploadFile, document_type: str, prompt: str) -> dict:
    file_name = file.filename or "unknown_file"
    page_images_base64 = await _extract_pages_from_upload(file)
    total_pages = len(page_images_base64)
    pages = []

    db = SessionLocal()
    try:
        for idx, image_base64 in enumerate(page_images_base64, start=1):
            extracted_text = call_vision_model_raw(
                prompt,
                image_base64,
                api_endpoint=f"/extract/text/{document_type}",
                file_name=file_name,
            ).strip()
            extracted_text = _clean_ocr_text(extracted_text)

            pages.append({
                "page_number": idx,
                "extracted_text": extracted_text,
            })

        ocr_result = {"pages": pages}
        process_text_document_ocr(
            db,
            {
                "document_type": document_type,
                "file_name": file_name,
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
        raise HTTPException(status_code=500, detail=f"Text document extraction failed: {str(exc)}")
    finally:
        db.close()

    return {
        "document_type": document_type,
        "file_name": file_name,
        "total_pages": total_pages,
        "pages": pages,
    }
