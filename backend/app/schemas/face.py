from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class FaceVerificationResponse(BaseModel):
    success: bool
    verification_id: str
    outcome: str # matched, not_matched, requires_review, error
    similarity_score: float
    match_percentage: float
    threshold: float
    final_decision: str
    risk_level: str
    risk_score: int
    risk_reasons: List[str]
    notes: str
