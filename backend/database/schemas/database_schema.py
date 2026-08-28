from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import date, datetime
from database.models.document import DocumentStatus

class PersonBase(BaseModel):
    full_name: str
    date_of_birth: date
    nationality: str
    gender: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonOut(PersonBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    document_type: str
    document_number: str
    issuing_country: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: DocumentStatus = DocumentStatus.ACTIVE

class DocumentCreate(DocumentBase):
    person_id: UUID4

class DocumentOut(DocumentBase):
    id: UUID4
    person_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
