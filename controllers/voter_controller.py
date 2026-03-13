from fastapi import UploadFile

from extractors.voter_extractor import extract_voter_id as _extract_voter_id


async def extract_voter_id(file: UploadFile):
    """Controller wrapper to keep route layer consistent with PAN/Aadhaar."""
    return await _extract_voter_id(file)
