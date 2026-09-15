"""
Document Screening Coordination Service
Orchestrates:
1. File validation & decoding (via image_preprocessing)
2. Quality scoring (sharpness, exposure, dimensions, glare)
3. Skew correction & contrast enhancement (CLAHE)
4. OCR extraction & line confidence calculation (PaddleOCR / optical detection)
5. ICAO 9303 MRZ parsing & check digit verification
6. Government verification provider & database registry matching
7. Date & status rules validation
8. Tampering & forensic analysis
9. Rule-based document decision (VERIFIED / REQUIRES_REVIEW / NOT_VERIFIED / etc.)
10. Risk assessment index calculation
11. PostgreSQL transaction persistence
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
import cv2

from app.config import settings
from app.utils.security import validate_image_bytes, generate_safe_filename, cleanup_temp_files
from app.services.image_preprocessing import (
    validate_and_decode_image,
    assess_optical_quality,
    preprocess_document_for_ocr
)
from app.services.ocr_service import run_ocr_on_image
from app.services.mrz_service import parse_and_validate_mrz
from app.services.matching_service import match_document_against_database
from app.services.validation_service import validate_document_rules
from app.services.tampering_service import analyze_document_tampering
from app.services.decision_service import evaluate_document_decision
from app.services.risk_service import calculate_risk_assessment
from database.models import VerificationRecord, Document

def process_document_upload(
    db: Session,
    file_bytes: bytes,
    document_type: str,
    original_filename: str
) -> Dict[str, Any]:
    """
    Execute complete end-to-end document verification pipeline.
    """
    # 0. Routine maintenance: purge stale temporary files
    cleanup_temp_files(settings.TEMP_DIR)

    # 1. Validate magic bytes header directly from content
    is_valid_format, mime_or_err = validate_image_bytes(file_bytes)
    if not is_valid_format:
        return {
            "success": False,
            "error": mime_or_err,
            "status_code": 400
        }

    # 2. Safely decode image using image preprocessing service
    img_bgr, decode_err = validate_and_decode_image(file_bytes)
    if img_bgr is None:
        return {
            "success": False,
            "error": decode_err or "Corrupted image file.",
            "status_code": 400
        }

    # 3. Optical quality assessment and preprocessing (deskew, CLAHE contrast)
    enhanced_img, prep_meta = preprocess_document_for_ocr(img_bgr)
    quality_report = prep_meta["quality"]

    # 4. Generate safe filename & save image to secure temporary storage directory
    ext = os.path.splitext(original_filename)[1]
    safe_name = generate_safe_filename(ext)
    file_path = os.path.join(settings.TEMP_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # 5. Run OCR & Field Extraction on preprocessed image
    ocr_res = run_ocr_on_image(enhanced_img, document_type=document_type)
    ocr_res["document_image_filename"] = safe_name

    # 6. Parse MRZ & Check digits
    mrz_res = ocr_res.get("mrz_result")
    if not mrz_res or not mrz_res.get("detected"):
        mrz_raw = ocr_res["fields"].get("mrz_raw")
        mrz_res = parse_and_validate_mrz(mrz_raw)

    # If MRZ found fields, supplement any missing visual fields
    if mrz_res.get("detected") and mrz_res.get("fields"):
        for k in ["full_name", "document_number", "nationality", "gender", "sex", "date_of_birth", "expiry_date"]:
            val = mrz_res["fields"].get(k)
            if isinstance(val, dict):
                val = val.get("value")
            if not ocr_res["fields"].get(k) and val:
                ocr_res["fields"][k] = val


    # 7. Database / Government Registry Matching
    matching_res = match_document_against_database(
        db=db,
        extracted_fields=ocr_res["fields"],
        document_type=document_type
    )

    # 8. Document Date & Status Validation Rules
    validation_res = validate_document_rules(
        extracted_fields=ocr_res["fields"],
        matching_result=matching_res,
        mrz_result=mrz_res
    )

    # 9. Tampering & Forensic Analysis
    tampering_res = analyze_document_tampering(file_bytes, img_bgr)

    # 10. Document Decision Engine
    decision, decision_reasons = evaluate_document_decision(
        ocr_result=ocr_res,
        matching_result=matching_res,
        validation_result=validation_res,
        mrz_result=mrz_res,
        tampering_result=tampering_res
    )

    # 11. Risk Assessment Engine
    risk_res = calculate_risk_assessment(
        document_decision=decision,
        matching_result=matching_res,
        ocr_result=ocr_res,
        validation_result=validation_res,
        tampering_result=tampering_res
    )

    # 12. Create or Update Persistent Document Record in Database using Real Extracted Info Only
    matched_doc_id = matching_res.get("matched_record", {}).get("document_id") if matching_res.get("matched_record") else None
    doc_record = None

    extracted_doc_num = ocr_res["fields"].get("document_number")
    extracted_country = ocr_res["fields"].get("nationality")
    extracted_issue = ocr_res["fields"].get("issue_date")
    extracted_expiry = ocr_res["fields"].get("expiry_date")

    try:
        if matched_doc_id:
            doc_record = db.query(Document).filter(Document.id == matched_doc_id).first()

        if not doc_record and extracted_doc_num:
            doc_record = db.query(Document).filter(Document.document_number == str(extracted_doc_num).strip()).first()

        if doc_record:
            if extracted_country and not doc_record.issuing_country:
                doc_record.issuing_country = extracted_country
            if extracted_issue and not doc_record.issue_date:
                doc_record.issue_date = extracted_issue
            if extracted_expiry and not doc_record.expiry_date:
                doc_record.expiry_date = extracted_expiry
            doc_record.updated_at = datetime.utcnow()
        else:
            # Create a new Document record with real extracted/available data only
            doc_record = Document(
                id=str(uuid.uuid4()),
                person_id=None,
                document_type=document_type,
                document_number=extracted_doc_num,
                issuing_country=extracted_country,
                issue_date=extracted_issue,
                expiry_date=extracted_expiry,
                status="active" if decision == "VERIFIED" else "pending_review",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(doc_record)
            db.flush()
    except Exception as db_err:
        db.rollback()
        # Fallback: retrieve if existed or create with a unique temporary identifier
        if extracted_doc_num:
            doc_record = db.query(Document).filter(Document.document_number == str(extracted_doc_num).strip()).first()
        if not doc_record:
            doc_record = Document(
                id=str(uuid.uuid4()),
                person_id=None,
                document_type=document_type,
                document_number=extracted_doc_num or f"DOC-{uuid.uuid4().hex[:8].upper()}",
                issuing_country=extracted_country,
                issue_date=extracted_issue,
                expiry_date=extracted_expiry,
                status="pending_review",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            try:
                db.add(doc_record)
                db.flush()
            except Exception:
                db.rollback()

    actual_doc_id = doc_record.id if doc_record else str(uuid.uuid4())

    # 13. Create Persistent Verification Record in Database
    verification_id = f"IDF-2026-{uuid.uuid4().hex[:5].upper()}"

    # Face verification eligibility: strictly locked if document is not accepted/verified!
    can_proceed_to_face = (decision == "VERIFIED")

    try:
        record = VerificationRecord(
            id=verification_id,
            document_id=actual_doc_id if doc_record else None,
            verification_status=decision,
            risk_level=risk_res["risk_level"],
            risk_score=risk_res["risk_score"],
            risk_reasons=risk_res["reasons"],
            ocr_data=ocr_res,
            matching_data=matching_res,
            validation_data=validation_res,
            tampering_data=tampering_res,
            face_data={"status": "PENDING", "eligible": can_proceed_to_face},
            document_decision=decision,
            final_decision=decision if not can_proceed_to_face else "PENDING_FACE_VERIFICATION",
            officer_notes="; ".join(decision_reasons),
            created_at=datetime.utcnow()
        )

        db.add(record)
        db.commit()
    except Exception as rec_err:
        db.rollback()

    return {
        "success": True,
        "verification_id": verification_id,
        "document_id": actual_doc_id,
        "document_type": document_type,
        "image_quality": quality_report,
        "preprocessing_metadata": prep_meta,
        "document_status": decision,
        "can_proceed_to_face": can_proceed_to_face,
        "risk_level": risk_res["risk_level"],
        "risk_score": risk_res["risk_score"],
        "risk_reasons": risk_res["reasons"],
        "ocr_result": {
            "status": ocr_res.get("status", "success"),
            "fields": ocr_res["fields"],
            "name": ocr_res["fields"].get("name", {}),
            "visual_name": ocr_res["fields"].get("visual_name", {}),
            "mrz_name": ocr_res["fields"].get("mrz_name", {}),
            "name_consistency": ocr_res["fields"].get("name_consistency", {}),
            "text": ocr_res["text"],
            "full_text": ocr_res["full_text"],
            "text_lines": ocr_res.get("text_lines", []),
            "confidence": ocr_res["confidence"],
            "average_confidence": ocr_res["average_confidence"],
            "field_confidence": ocr_res.get("field_confidence", {}),
            "quality_score": ocr_res.get("quality_score", "GOOD"),
            "quality_reason": ocr_res.get("quality_reason", ""),
            "processing_time_ms": ocr_res.get("processing_time_ms", 0.0),
            "engine": ocr_res["engine"]
        },
        "mrz_result": mrz_res,
        "matching_result": matching_res,
        "validation_result": validation_res,
        "tampering_result": {
            "tampering_detected": tampering_res["tampering_detected"],
            "confidence": tampering_res["confidence"],
            "requires_review": tampering_res["requires_review"],
            "indicators": tampering_res["indicators"],
            "metadata_analysis": tampering_res["metadata_analysis"],
            "ela_analysis": tampering_res["ela_analysis"]
        },
        "decision_reasons": decision_reasons
    }
