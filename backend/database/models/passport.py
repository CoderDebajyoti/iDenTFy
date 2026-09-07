import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Passport(Base):
    __tablename__ = "passports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    passport_number = Column(String(50), nullable=False, index=True)
    nationality = Column(String(3), nullable=False)
    date_of_birth = Column(String(10), nullable=False)
    gender = Column(String(1), nullable=False)
    issue_date = Column(String(10), nullable=False)
    expiry_date = Column(String(10), nullable=False)
    mrz_line_1 = Column(String(44), nullable=True)
    mrz_line_2 = Column(String(44), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="passport_details")
