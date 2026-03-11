import uuid

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func
from db.database import Base


def generate_alphanumeric_id(length: int = 10) -> str:
    return str(uuid.uuid4())


class AccountForm(Base):
    __tablename__ = "account_forms"
    
    id = Column(String(36), primary_key=True, default=generate_alphanumeric_id)
    branch_code = Column(String(10))
    account_number = Column(String(20))
    customer_name = Column(String(150))
    pan_number = Column(String(20))
    mobile_number = Column(String(20))
    form_status = Column(String(30), default="DRAFT")
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime, onupdate=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_approved = Column(Boolean, default=False)


class AccountFormPage(Base):
    __tablename__ = "account_form_pages"
    
    id = Column(String(36), primary_key=True, default=generate_alphanumeric_id)
    form_id = Column(String(36), ForeignKey("account_forms.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_data = Column(Text, nullable=False)
    is_verified = Column(String(1), default="N")
    verified_by = Column(String(100))
    verified_date = Column(DateTime)
    created_by = Column(String(100))
    created_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_date = Column(DateTime, onupdate=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_approved = Column(Boolean, default=False)
