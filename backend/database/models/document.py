from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum
from database.base import Base

class DocumentStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    BLACKLISTED = "blacklisted"
    SUSPENDED = "suspended"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)
    document_type = Column(String, nullable=False, index=True)
    document_number = Column(String, nullable=False, unique=True, index=True)
    issuing_country = Column(String, nullable=False)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.ACTIVE, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    person = relationship("Person", backref="documents")
    passport = relationship("Passport", back_populates="document", uselist=False)
    visas = relationship("Visa", back_populates="document")
