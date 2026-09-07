import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String(36), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False) # passport, identity_card, residence_permit, driver_license
    document_number = Column(String(100), nullable=False, unique=True, index=True)
    issuing_country = Column(String(3), nullable=False) # ISO 3166-1 alpha-3
    issue_date = Column(String(10), nullable=False) # Format: YYYY-MM-DD
    expiry_date = Column(String(10), nullable=False) # Format: YYYY-MM-DD
    status = Column(String(30), nullable=False, default="active") # active, expired, revoked, blacklisted, suspended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    person = relationship("Person", back_populates="documents")
    passport_details = relationship("Passport", back_populates="document", uselist=False, cascade="all, delete-orphan")
    visa_records = relationship("Visa", back_populates="document", cascade="all, delete-orphan")
    verification_records = relationship("VerificationRecord", back_populates="document")
