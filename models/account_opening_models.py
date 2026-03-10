import uuid
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func
from db.database import Base


class AccountForm(Base):
    __tablename__ = "account_forms"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(10))
    account_number = Column(String(20))
    customer_name = Column(String(150))
    pan_number = Column(String(20))
    mobile_number = Column(String(20))
    form_status = Column(String(30), default="DRAFT")
    created_by = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=func.now())
    is_approved = Column(Boolean, default=False)


class AccountFormPage(Base):
    __tablename__ = "account_form_pages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id = Column(String(36), ForeignKey("account_forms.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_data = Column(Text, nullable=False)
    created_by = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=func.now())
    is_approved = Column(Boolean, default=False)
