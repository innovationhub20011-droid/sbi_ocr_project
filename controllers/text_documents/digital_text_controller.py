from fastapi import UploadFile

from extractors.text_documents.digital_text_extractor import (
    extract_digital_text as _extract_digital_text,
    get_all_digital_text_ocr as _get_all_digital_text_ocr,
)


async def extract_digital_text(file: UploadFile) -> dict:
    return await _extract_digital_text(file)


def get_all_digital_text_ocr() -> dict:
    return _get_all_digital_text_ocr()
