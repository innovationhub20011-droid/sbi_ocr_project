from fastapi import UploadFile

from extractors.driving_extractor import extract_driving_license as _extract_driving_license


async def extract_driving_license(file: UploadFile):
    """Controller wrapper to keep route layer consistent with PAN/Aadhaar."""
    return await _extract_driving_license(file)
