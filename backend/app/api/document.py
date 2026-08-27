import os
import uuid
import logging
import cv2
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from PIL import Image
import io

from app.schemas.verification import ModuleStatus, DocumentUploadResponse
from app.utils.image_utils import assess_image_quality, preprocess_image
from app.services.ocr_service import OCRService

logger = logging.getLogger("document_api")

router = APIRouter()

# Configuration and Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_DOC_TYPES = {"passport", "identity_card", "residence_permit", "driver_license"}

@router.get("/status", response_model=ModuleStatus)
def get_document_status():
    return ModuleStatus(
        module="document-verification",
        status="not_implemented",
        phase=1
    )

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    document_type: str = Form(...),
    document_file: UploadFile = File(...)
):
    """
    Endpoint to upload a document, validate it, check image quality,
    preprocess the image, and perform OCR extraction.
    """
    logger.info(f"Upload request received. Doc Type: {document_type}, Filename: {document_file.filename}")
    
    # 1. Validate document type
    if document_type not in ALLOWED_DOC_TYPES:
        logger.warning(f"Invalid document type requested: {document_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Allowed types: {list(ALLOWED_DOC_TYPES)}"
        )
        
    # 2. Check for empty file upload
    if not document_file or not document_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty or missing file upload."
        )
        
    # 3. Read content and validate size
    try:
        content = await document_file.read()
    except Exception as e:
        logger.error(f"Error reading upload file content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded file."
        )
        
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"Upload size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes.")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 10 MB."
        )
        
    # 4. Validate MIME Type and Filename Extension
    content_type = document_file.content_type
    file_ext = os.path.splitext(document_file.filename)[1].lower()
    
    if content_type not in ALLOWED_MIME_TYPES or file_ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Unsupported file MIME type: {content_type} or Extension: {file_ext}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported format. Only JPEG (.jpg, .jpeg) and PNG (.png) images are allowed."
        )
        
    # 5. Deep content validation using Pillow to decode image headers
    try:
        pil_img = Image.open(io.BytesIO(content))
        pil_img.verify()
        actual_format = pil_img.format.lower()
        if actual_format not in {"jpeg", "png"}:
            logger.warning(f"Pillow header verify failed: Actual content is {actual_format}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "error_code": "INVALID_IMAGE",
                    "message": f"The uploaded file format '{actual_format}' is not supported."
                }
            )
    except Exception as e:
        logger.warning(f"Pillow decoding failure verifying content: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "error_code": "INVALID_IMAGE",
                "message": "The uploaded file could not be decoded as a valid image."
            }
        )
        
    # 6. Save file temporarily with generated safe filename
    os.makedirs("uploads", exist_ok=True)
    temp_uuid = uuid.uuid4().hex[:8]
    safe_name = f"{temp_uuid}_document{file_ext}"
    temp_path = os.path.join("uploads", safe_name)
    
    try:
        with open(temp_path, "wb") as f:
            f.write(content)
        logger.info(f"Temporary file saved to {temp_path}")
    except Exception as e:
        logger.error(f"Error saving temp file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded document locally."
        )
        
    # Run the remaining pipeline and clean up the file
    try:
        # Decode image with OpenCV
        image = cv2.imread(temp_path)
        if image is None or image.size == 0:
            logger.error(f"OpenCV failed to read decoded image from path {temp_path}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "error_code": "INVALID_IMAGE",
                    "message": "The uploaded file could not be decoded as a valid image."
                }
            )
            
        # 7. Quality Assessment
        logger.info("Executing image quality checks...")
        quality_info = assess_image_quality(image)
        logger.info(f"Image quality metrics: {quality_info}")
        
        # 8. Preprocessing
        logger.info("Executing image preprocessing...")
        preprocessed = preprocess_image(image)
        
        # 9. OCR Extraction
        logger.info("Executing OCR engine...")
        ocr_results = OCRService.run_ocr(preprocessed)
        logger.info("OCR execution successful.")
        
        return DocumentUploadResponse(
            status="success",
            document_type=document_type,
            image_quality=quality_info,
            ocr=ocr_results
        )
        
    except Exception as e:
        logger.error(f"Internal processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal processing error occurred."
        )
    finally:
        # Clean up temporary file from uploads directory
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Cleaned up temporary file {temp_path}")
            except Exception as ex:
                logger.error(f"Failed to delete temp file {temp_path}: {str(ex)}")
