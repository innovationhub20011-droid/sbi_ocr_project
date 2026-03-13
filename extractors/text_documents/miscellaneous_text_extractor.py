from fastapi import UploadFile

from prompts.misc_text_prompt import MISC_TEXT_PROMPT
from services.document_service import retrieve_miscellaneous_text_details
from services.text_documents_service import extract_text_document
from db.database import SessionLocal


async def extract_misc_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "miscellaneous_text", MISC_TEXT_PROMPT)


def get_all_miscellaneous_text_ocr() -> dict:
    db = SessionLocal()
    try:
        records = retrieve_miscellaneous_text_details(db)
        return {"records": records}
    finally:
        db.close()
