import os
import cv2
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.utils.security import validate_image_bytes, generate_safe_filename
from app.utils.image_utils import decode_image_bytes
from app.services.face_service import perform_face_verification
from app.services.risk_service import calculate_risk_assessment
from database.database import get_db
from database.models import VerificationRecord

router = APIRouter(prefix="/face", tags=["Face Biometrics"])

@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Biometric 1:1 Face Verification",
    description="Cross-matches live subject face against document portrait. STRICT GATE: Rejects execution if document verification did not pass."
)
async def verify_face(
    verification_id: str = Form(..., description="Active screening verification ID (e.g., IDF-2026-XXXXX)"),
    face_file: UploadFile = File(..., description="Live subject camera capture or photo (JPEG, PNG < 10MB)"),
    db: Session = Depends(get_db)
):
    # 1. Lookup verification record
    record = db.query(VerificationRecord).filter(VerificationRecord.id == verification_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification record '{verification_id}' not found."
        )

    # 2. STRICT SECURITY GATE: Enforce sequential verification order
    if record.verification_status != "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Face verification blocked: Document screening status is '{record.verification_status}'. "
                "Biometric face matching can only be performed after document verification is completed successfully."
            )
        )

    # 3. Read live face image
    face_bytes = await face_file.read()
    if len(face_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Face image file is empty.")

    is_valid_format, mime_err = validate_image_bytes(face_bytes)
    if not is_valid_format:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mime_err)

    live_img_bgr, decode_err = decode_image_bytes(face_bytes)
    if live_img_bgr is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=decode_err or "Invalid face image.")

    # 4. Locate stored document image from disk
    doc_files = [
        os.path.join(settings.DOCUMENTS_DIR, f)
        for f in os.listdir(settings.DOCUMENTS_DIR)
        if os.path.isfile(os.path.join(settings.DOCUMENTS_DIR, f))
    ]

    # Use the most recent uploaded document file or first available
    doc_img_bgr = None
    if doc_files:
        # Sort by modification time descending
        doc_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        doc_img_bgr = cv2.imread(doc_files[0])

    if doc_img_bgr is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored document image not found for biometric cross-match."
        )

    # 5. Save live face image securely
    ext = os.path.splitext(face_file.filename or "face.jpg")[1]
    safe_face_name = generate_safe_filename(ext)
    face_save_path = os.path.join(settings.FACES_DIR, safe_face_name)
    with open(face_save_path, "wb") as f:
        f.write(face_bytes)

    # 6. Execute biometric comparison
    face_result = perform_face_verification(doc_img_bgr, live_img_bgr)

    if not face_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=face_result.get("error", "Biometric face verification error.")
        )

    outcome = face_result["outcome"] # matched | not_matched | requires_review

    # 7. Update final decision and risk
    if outcome == "matched":
        final_decision = "VERIFIED"
    elif outcome == "requires_review":
        final_decision = "REQUIRES_REVIEW"
    else:
        final_decision = "VERIFICATION_FAILED"

    # Recalculate complete risk assessment including face signals
    risk_update = calculate_risk_assessment(
        document_decision=record.document_decision or "VERIFIED",
        matching_result=record.matching_data or {},
        ocr_result=record.ocr_data or {},
        validation_result=record.validation_data or {},
        tampering_result=record.tampering_data or {},
        face_result=face_result
    )

    # Update database record
    record.face_data = face_result
    record.final_decision = final_decision
    record.risk_level = risk_update["risk_level"]
    record.risk_score = risk_update["risk_score"]
    record.risk_reasons = risk_update["reasons"]

    db.commit()

    return {
        "success": True,
        "verification_id": verification_id,
        "outcome": outcome,
        "similarity_score": face_result["similarity_score"],
        "match_percentage": face_result["match_percentage"],
        "threshold": face_result["threshold"],
        "final_decision": final_decision,
        "risk_level": risk_update["risk_level"],
        "risk_score": risk_update["risk_score"],
        "risk_reasons": risk_update["reasons"],
        "notes": face_result["notes"]
    }
