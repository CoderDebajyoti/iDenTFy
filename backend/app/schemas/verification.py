from pydantic import BaseModel
from typing import List

class ModuleStatus(BaseModel):
    """
    Schema for indicating implementation/running status of a module.
    """
    module: str
    status: str
    phase: int

class OCRTextItem(BaseModel):
    """
    Individual text region detected by OCR.
    """
    text: str
    confidence: float
    bounding_box: List[List[int]]

class OCRData(BaseModel):
    """
    Structured OCR results.
    """
    text: List[OCRTextItem]
    full_text: str
    average_confidence: float

class ImageQualityInfo(BaseModel):
    """
    Image quality metrics and status ratings.
    """
    width: int
    height: int
    blur_score: float
    blur_status: str
    brightness: float
    brightness_status: str
    resolution_status: str

class DocumentUploadResponse(BaseModel):
    """
    Response model for document uploads containing OCR results and image quality assessment.
    """
    status: str
    document_type: str
    image_quality: ImageQualityInfo
    ocr: OCRData
