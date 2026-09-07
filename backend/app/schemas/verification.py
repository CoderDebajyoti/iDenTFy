from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class VerificationHistoryItem(BaseModel):
    id: str
    timestamp: str
    document_type: str
    holder_name: str
    document_number: str
    nationality: str
    status: str
    risk_level: str
    risk_score: Optional[int] = None
    final_decision: Optional[str] = None

class VerificationHistoryResponse(BaseModel):
    success: bool
    total: int
    items: List[VerificationHistoryItem]

class SystemHealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str
    timestamp: str
