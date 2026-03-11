import uuid

from sqlalchemy import Column, Integer, String, DateTime, Text, func

from db.database import Base


def generate_alphanumeric_id(length: int = 10) -> str:
    return str(uuid.uuid4())


class PanCardDetails(Base):
    __tablename__ = "pan_card_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    pan_number = Column(String(10), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    father_name = Column(String(255))
    date_of_birth = Column(String(20))
    pan_type = Column(String(50))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class AadhaarCardDetails(Base):
    __tablename__ = "aadhaar_card_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    aadhaar_number = Column(String(12), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    date_of_birth = Column(String(20))
    gender = Column(String(20))
    address = Column(String(500))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class PassportDetails(Base):
    __tablename__ = "passport_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    passport_number = Column(String(20), unique=True, nullable=True, index=True)
    surname = Column(String(255))
    given_names = Column(String(255))
    nationality = Column(String(100))
    sex = Column(String(20))
    date_of_birth = Column(String(20))
    place_of_birth = Column(String(255))
    date_of_issue = Column(String(20))
    date_of_expiry = Column(String(20))
    place_of_issue = Column(String(255))
    father_name = Column(String(255))
    mother_name = Column(String(255))
    address = Column(String(1000))
    pin_code = Column(String(20))
    file_number = Column(String(50))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class DrivingLicenseDetails(Base):
    __tablename__ = "driving_license_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    driving_licence_number = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(255))
    father_name = Column(String(255))
    date_of_birth = Column(String(20))
    date_of_issue = Column(String(20))
    valid_till_nt = Column(String(20))
    valid_till_tr = Column(String(20))
    address = Column(String(1000))
    blood_group = Column(String(20))
    class_of_vehicle = Column(String(255))
    issuing_authority = Column(String(255))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class VoterIdDetails(Base):
    __tablename__ = "voter_id_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    epic_number = Column(String(20), unique=True, nullable=True, index=True)
    name = Column(String(255))
    father_name = Column(String(255))
    gender = Column(String(20))
    date_of_birth = Column(String(20))
    address = Column(String(1000))
    electoral_registration_officer = Column(String(255))
    assembly_constituency = Column(String(255))
    download_date = Column(String(20))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class HandwrittenTextOcrDetails(Base):
    __tablename__ = "handwritten_text_ocr_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    document_type = Column(String(100), nullable=False)
    file_name = Column(String(255))
    ocr_result = Column(Text, nullable=False)
    total_pages = Column(Integer, nullable=False)
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class DigitalTextOcrDetails(Base):
    __tablename__ = "digital_text_ocr_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    document_type = Column(String(100), nullable=False)
    file_name = Column(String(255))
    ocr_result = Column(Text, nullable=False)
    total_pages = Column(Integer, nullable=False)
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class MiscellaneousTextOcrDetails(Base):
    __tablename__ = "miscellaneous_text_ocr_details"

    id = Column(String(36), primary_key=True, index=True, default=generate_alphanumeric_id)
    document_type = Column(String(100), nullable=False)
    file_name = Column(String(255))
    ocr_result = Column(Text, nullable=False)
    total_pages = Column(Integer, nullable=False)
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)