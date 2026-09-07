import os
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.services.document_service import process_document_upload
from database.database import get_db
from database.models import Document

router = APIRouter(prefix="/document", tags=["Document Operations"])

SUPPORTED_TYPES = {"passport", "identity_card", "residence_permit", "driver_license"}

@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload and screen identity document",
    description="Accepts identity document image and executes image quality check, OCR, MRZ validation, database matching, and tampering forensics."
)
async def upload_document(
    document_type: str = Form(..., description="passport | identity_card | residence_permit | driver_license"),
    document_file: UploadFile = File(..., description="Document image file (JPEG, JPG, PNG < 10MB)"),
    db: Session = Depends(get_db)
):
    # Validate document_type
    clean_type = document_type.strip().lower()
    if clean_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document_type '{document_type}'. Supported: {', '.join(SUPPORTED_TYPES)}"
        )

    # Read bytes and check size
    file_bytes = await document_file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty (0 bytes).")

    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of 10 MB ({round(len(file_bytes) / (1024*1024), 2)} MB received)."
        )

    # Execute processing pipeline
    result = process_document_upload(
        db=db,
        file_bytes=file_bytes,
        document_type=clean_type,
        original_filename=document_file.filename or "upload.jpg"
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result.get("error", "Document processing error.")
        )

    return result

@router.get(
    "/{document_id}",
    summary="Retrieve registered document metadata",
    description="Looks up a registered document in the registry by UUID."
)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document ID '{document_id}' not found.")

    person = doc.person
    return {
        "id": doc.id,
        "document_type": doc.document_type,
        "document_number": doc.document_number,
        "issuing_country": doc.issuing_country,
        "issue_date": doc.issue_date,
        "expiry_date": doc.expiry_date,
        "status": doc.status,
        "holder": {
            "full_name": person.full_name if person else None,
            "date_of_birth": person.date_of_birth if person else None,
            "nationality": person.nationality if person else None
        }
    }
