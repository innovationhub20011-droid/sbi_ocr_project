from sqlalchemy import Column, Integer, String, DateTime, Text, func

from db.database import Base


class PanCardDetails(Base):
    __tablename__ = "pan_card_details"

    id = Column(Integer, primary_key=True, index=True)
    pan_number = Column(String(10), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    father_name = Column(String(255))
    date_of_birth = Column(String(20))
    pan_type = Column(String(50))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class AadhaarCardDetails(Base):
    __tablename__ = "aadhaar_card_details"

    id = Column(Integer, primary_key=True, index=True)
    aadhaar_number = Column(String(12), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    date_of_birth = Column(String(20))
    gender = Column(String(20))
    address = Column(String(500))
    ocr_source = Column(String(100))
    is_verified = Column(String(1), default="N")
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime)


class HandwrittenTextOcrDetails(Base):
    __tablename__ = "handwritten_text_ocr_details"

    id = Column(Integer, primary_key=True, index=True)
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

    id = Column(Integer, primary_key=True, index=True)
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

    id = Column(Integer, primary_key=True, index=True)
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