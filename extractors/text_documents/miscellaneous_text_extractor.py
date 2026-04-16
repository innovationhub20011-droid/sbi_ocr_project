from fastapi import UploadFile

from prompts.misc_text_prompt import MISC_TEXT_PROMPT
from services.text_services import retrieve_miscellaneous_text_details
from services.text_documents_service import extract_text_document


async def extract_misc_text(file: UploadFile) -> dict:
    return await extract_text_document(file, "miscellaneous_text", MISC_TEXT_PROMPT)


def get_all_miscellaneous_text_ocr() -> dict:
    return {"records": retrieve_miscellaneous_text_details()}
