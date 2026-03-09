import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

PAN_TYPE_MAP = {
    "P": "INDIVIDUAL",
    "C": "COMPANY",
    "H": "HUF",
    "F": "FIRM",
    "A": "AOP",
    "T": "TRUST",
    "B": "BOI",
    "L": "LOCAL_AUTHORITY",
    "J": "ARTIFICIAL_JURIDICAL_PERSON",
    "G": "GOVERNMENT",
}


class PanCreate(BaseModel):
    pan_number: str
    full_name: Optional[str]
    father_name: Optional[str]
    date_of_birth: Optional[str]

    @field_validator("pan_number")
    @classmethod
    def validate_pan(cls, v):
        v = v.strip().upper().replace(" ", "")
        if not re.match(PAN_REGEX, v):
            raise ValueError("Invalid PAN format")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def normalize_date(cls, v):
        if not v:
            return None
        formats = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y")
        for fmt in formats:
            try:
                return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError("Invalid date format")

    def derive_pan_type(self):
        return PAN_TYPE_MAP.get(self.pan_number[3])


class AadhaarCreate(BaseModel):
    aadhaar_number: str
    full_name: Optional[str]
    date_of_birth: Optional[str]
    gender: Optional[str]
    address: Optional[str]

    @field_validator("aadhaar_number")
    @classmethod
    def validate_aadhaar(cls, v):
        digits = re.sub(r"[^0-9]", "", v)
        if len(digits) != 12:
            raise ValueError("Invalid Aadhaar number")
        return digits
    
class RawTextCreate(BaseModel):
    document_text: str
    language: Optional[str] = "en"
    ocr_source: Optional[str] = "vision_model"

    @field_validator("document_text")
    @classmethod
    def validate_document_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Document text cannot be empty")

        if len(v) < 5:
            raise ValueError("Extracted text is too short to be valid")

        return " ".join(v.split())