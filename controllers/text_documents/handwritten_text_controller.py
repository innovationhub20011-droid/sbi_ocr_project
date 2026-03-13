from fastapi import UploadFile

from extractors.text_documents.handwritten_text_extractor import (
    extract_handwritten_text as _extract_handwritten_text,
    get_all_handwritten_text_ocr as _get_all_handwritten_text_ocr,
)


async def extract_handwritten_text(file: UploadFile) -> dict:
    return await _extract_handwritten_text(file)


def get_all_handwritten_text_ocr() -> dict:
    return _get_all_handwritten_text_ocr()
