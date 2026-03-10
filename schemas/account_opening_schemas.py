
import re
from typing import Optional
from pydantic import BaseModel, field_validator

PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

class AccountFormCreate(BaseModel):
    """Pydantic model for creating account opening form main entry"""
    branch_code: Optional[str] = None
    account_number: Optional[str] = None
    customer_name: Optional[str] = None
    pan_number: Optional[str] = None
    mobile_number: Optional[str] = None
    form_status: str = "OCR_PENDING"
    created_by: str = "system"



class AccountFormPageCreate(BaseModel):
    """Pydantic model for creating account opening form page entry"""
    form_id: str  # UUID as string
    page_number: int
    page_data: str  # JSON string containing the extracted data
    created_by: str = "system"

    @field_validator("page_data")
    @classmethod
    def validate_page_data(cls, v):
        if not v or not v.strip():
            raise ValueError("Page data cannot be empty")
        return v

    @field_validator("page_number")
    @classmethod
    def validate_page_number(cls, v):
        if v < 1:
            raise ValueError("Page number must be positive")
        return v