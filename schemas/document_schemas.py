import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


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


class PassportCreate(BaseModel):
    passport_number: Optional[str] = None
    surname: Optional[str] = None
    given_names: Optional[str] = None
    nationality: Optional[str] = None
    sex: Optional[str] = None
    date_of_birth: Optional[str] = None
    place_of_birth: Optional[str] = None
    date_of_issue: Optional[str] = None
    date_of_expiry: Optional[str] = None
    place_of_issue: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    address: Optional[str] = None
    pin_code: Optional[str] = None
    file_number: Optional[str] = None


class DrivingLicenseCreate(BaseModel):
    driving_licence_number: Optional[str] = None
    name: Optional[str] = None
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    date_of_issue: Optional[str] = None
    valid_till_nt: Optional[str] = None
    valid_till_tr: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    class_of_vehicle: Optional[str] = None
    issuing_authority: Optional[str] = None


class VoterIdCreate(BaseModel):
    epic_number: Optional[str] = None
    name: Optional[str] = None
    father_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    electoral_registration_officer: Optional[str] = None
    assembly_constituency: Optional[str] = None
    download_date: Optional[str] = None
    
class TextDocumentOcrCreate(BaseModel):
    document_type: str
    ocr_result: dict
    total_pages: int
    file_name: Optional[str] = None
    ocr_source: Optional[str] = "vision_model"

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        allowed = {"handwritten_text", "digital_text", "miscellaneous_text"}
        normalized = (v or "").strip().lower()
        if normalized not in allowed:
            raise ValueError("Unsupported text document type")
        return normalized

    @field_validator("total_pages")
    @classmethod
    def validate_positive_number(cls, v):
        if v < 1:
            raise ValueError("Page numbers must be positive")
        return v

    @field_validator("ocr_result")
    @classmethod
    def validate_ocr_result(cls, v):
        if not isinstance(v, dict):
            raise ValueError("ocr_result must be a valid JSON object")

        pages = v.get("pages", [])
        if not isinstance(pages, list):
            raise ValueError("ocr_result.pages must be a list")

        return v