import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from database.database import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False, index=True)
    date_of_birth = Column(String(10), nullable=False) # Format: YYYY-MM-DD
    nationality = Column(String(3), nullable=False, index=True) # ISO 3166-1 alpha-3
    gender = Column(String(1), nullable=False) # M, F, X
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="person", cascade="all, delete-orphan")
