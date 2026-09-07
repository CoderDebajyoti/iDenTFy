import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database.database import Base

class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(String(50), primary_key=True) # e.g. IDF-2026-XXXXX
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    verification_status = Column(String(50), nullable=False, default="PROCESSING") # VERIFIED, REQUIRES_REVIEW, NOT_VERIFIED, EXPIRED, BLACKLISTED, SUSPENDED
    risk_level = Column(String(20), nullable=False, default="PENDING") # LOW, MEDIUM, HIGH, PENDING
    risk_score = Column(Integer, nullable=True) # 0 to 100
    risk_reasons = Column(JSON, nullable=True, default=list)

    # Detailed Forensic & Audit Signals
    ocr_data = Column(JSON, nullable=True)
    matching_data = Column(JSON, nullable=True)
    validation_data = Column(JSON, nullable=True)
    tampering_data = Column(JSON, nullable=True)
    face_data = Column(JSON, nullable=True)

    document_decision = Column(String(50), nullable=True)
    final_decision = Column(String(50), nullable=True)
    officer_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    document = relationship("Document", back_populates="verification_records")
