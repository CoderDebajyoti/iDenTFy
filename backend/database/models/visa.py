from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database.base import Base

class Visa(Base):
    __tablename__ = "visas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    visa_number = Column(String, nullable=False, unique=True, index=True)
    visa_type = Column(String, nullable=True)
    issuing_country = Column(String, nullable=False)
    entry_type = Column(String, nullable=True) # e.g. "Single", "Multiple"
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    stay_duration_days = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="visas")
