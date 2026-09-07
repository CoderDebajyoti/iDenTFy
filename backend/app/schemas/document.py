from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ImageQualitySchema(BaseModel):
    valid: bool
    width: int
    height: int
    blur_score: float
    brightness: float
    quality_rating: str
    notes: List[str] = []

class DocumentUploadResponse(BaseModel):
    success: bool
    verification_id: str
    document_id: Optional[str] = None
    document_type: str
    image_quality: ImageQualitySchema
    document_status: str
    can_proceed_to_face: bool
    risk_level: str
    risk_score: int
    risk_reasons: List[str]
    ocr_result: Dict[str, Any]
    mrz_result: Dict[str, Any]
    matching_result: Dict[str, Any]
    validation_result: Dict[str, Any]
    tampering_result: Dict[str, Any]
    decision_reasons: List[str]
