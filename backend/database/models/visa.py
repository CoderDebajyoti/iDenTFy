import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Visa(Base):
    __tablename__ = "visas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    visa_number = Column(String(50), nullable=False, unique=True, index=True)
    visa_type = Column(String(30), nullable=False) # tourist, business, student, transit, diplomat
    issuing_country = Column(String(3), nullable=False)
    entry_type = Column(String(20), nullable=False, default="single") # single, multiple
    valid_from = Column(String(10), nullable=False)
    valid_until = Column(String(10), nullable=False)
    stay_duration_days = Column(Integer, nullable=False, default=90)
    status = Column(String(30), nullable=False, default="valid") # valid, expired, revoked

    # Relationships
    document = relationship("Document", back_populates="visa_records")
