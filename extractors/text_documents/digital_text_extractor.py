from fastapi import UploadFile

from prompts.digital_text_prompt import DIGITAL_TEXT_PROMPT
from services.text_services import retrieve_digital_text_details
from services.text_documents_service import extract_text_document


async def extract_digital_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "digital_text", DIGITAL_TEXT_PROMPT)


def get_all_digital_text_ocr() -> dict:
    return {"records": retrieve_digital_text_details()}
