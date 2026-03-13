from fastapi import UploadFile

from extractors.text_documents.miscellaneous_text_extractor import (
    extract_misc_text as _extract_misc_text,
    get_all_miscellaneous_text_ocr as _get_all_miscellaneous_text_ocr,
)


async def extract_misc_text(file: UploadFile) -> dict:
    return await _extract_misc_text(file)


def get_all_miscellaneous_text_ocr() -> dict:
    return _get_all_miscellaneous_text_ocr()
