from fastapi import UploadFile

from extractors.passport_extractor import extract_passport as _extract_passport


async def extract_passport(file: UploadFile):
    """Controller wrapper to keep route layer consistent with PAN/Aadhaar."""
    return await _extract_passport(file)
