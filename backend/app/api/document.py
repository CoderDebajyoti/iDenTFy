import os
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.services.document_service import process_document_upload
from app.utils.security import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES
from database.database import get_db
from database.models import Document
from app.services.government.provider_manager import get_provider_manager

router = APIRouter(tags=["Document Operations"])

SUPPORTED_TYPES = {"passport", "identity_card", "residence_permit", "driver_license"}

@router.post(
    "/documents/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload and screen identity document",
    description="Accepts identity document image and executes image preprocessing, OCR, MRZ validation, database/provider matching, and tampering forensics."
)
@router.post(
    "/document/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload and screen identity document (alias)",
    include_in_schema=False
)
async def upload_document(
    document_type: str = Form(..., description="passport | identity_card | residence_permit | driver_license"),
    document_file: UploadFile = File(..., description="Document image file (JPEG, JPG, PNG < 10MB)"),
    db: Session = Depends(get_db)
):
    # 1. Validate document_type
    clean_type = document_type.strip().lower() if document_type else ""
    if clean_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document_type '{document_type}'. Supported: {', '.join(sorted(SUPPORTED_TYPES))}"
        )

    # 2. Validate file existence and filename
    if not document_file or not document_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing document file. Please select a valid document image."
        )

    # 3. Validate supported file extension
    _, ext = os.path.splitext(document_file.filename)
    clean_ext = ext.lower()
    if clean_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: invalid extension '{clean_ext or 'none'}'. Supported extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # 4. Validate MIME/content-type header if provided
    raw_content_type = (document_file.content_type or "").lower().strip()
    if raw_content_type and raw_content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: invalid MIME/content type '{document_file.content_type}'. Supported MIME types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
        )

    # 5. Read bytes and check size
    file_bytes = await document_file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty (0 bytes).")

    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of 10 MB ({round(len(file_bytes) / (1024*1024), 2)} MB received)."
        )

    # 6. Execute processing pipeline
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
    "/documents/{document_id}",
    summary="Retrieve registered document metadata",
    description="Looks up a registered document in the registry by UUID."
)
@router.get(
    "/document/{document_id}",
    summary="Retrieve registered document metadata (alias)",
    include_in_schema=False
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

@router.get(
    "/government/providers",
    summary="List Government Verification Providers",
    description="Lists all registered government verification providers and their connection statuses."
)
def list_government_providers():
    return get_provider_manager().list_providers()
