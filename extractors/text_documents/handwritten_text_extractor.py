from fastapi import UploadFile

from prompts.handwritten_text_prompt import HANDWRITTEN_TEXT_PROMPT
from services.document_service import retrieve_handwritten_text_details
from services.text_documents_service import extract_text_document
from db.database import SessionLocal


async def extract_handwritten_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "handwritten_text", HANDWRITTEN_TEXT_PROMPT)


def get_all_handwritten_text_ocr() -> dict:
    db = SessionLocal()
    try:
        records = retrieve_handwritten_text_details(db)
        return {"records": records}
    finally:
        db.close()
