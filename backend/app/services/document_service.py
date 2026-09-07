"""
Document Screening Coordination Service
Orchestrates:
1. File validation & decoding
2. Quality scoring (blur, exposure, dimensions)
3. OCR extraction & field parsing
4. MRZ checksum verification
5. Database registry matching
6. Date & status rules validation
7. Tampering & forensic analysis
8. Rule-based document decision
9. Risk assessment index calculation
10. Database audit record creation
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
import cv2

from app.config import settings
from app.utils.security import validate_image_bytes, generate_safe_filename
from app.utils.image_utils import decode_image_bytes, analyze_image_quality
from app.services.ocr_service import run_ocr_on_image
from app.services.mrz_service import parse_and_validate_mrz
from app.services.matching_service import match_document_against_database
from app.services.validation_service import validate_document_rules
from app.services.tampering_service import analyze_document_tampering
from app.services.decision_service import evaluate_document_decision
from app.services.risk_service import calculate_risk_assessment
from database.models import VerificationRecord

def process_document_upload(
    db: Session,
    file_bytes: bytes,
    document_type: str,
    original_filename: str
) -> Dict[str, Any]:
    """
    Execute complete end-to-end document verification pipeline.
    """
    # 1. Validate magic bytes and format
    is_valid_format, mime_or_err = validate_image_bytes(file_bytes)
    if not is_valid_format:
        return {
            "success": False,
            "error": mime_or_err,
            "status_code": 400
        }

    # 2. Decode image into OpenCV array
    img_bgr, decode_err = decode_image_bytes(file_bytes)
    if img_bgr is None:
        return {
            "success": False,
            "error": decode_err or "Corrupted image file.",
            "status_code": 400
        }

    # 3. Analyze optical quality
    quality_report = analyze_image_quality(img_bgr)
    if not quality_report["valid"]:
        # We record the warning but continue processing if not fatal
        pass

    # 4. Generate safe filename & save image to uploads directory
    ext = os.path.splitext(original_filename)[1]
    safe_name = generate_safe_filename(ext)
    file_path = os.path.join(settings.DOCUMENTS_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # 5. Run OCR & Field Extraction
    ocr_res = run_ocr_on_image(img_bgr, document_type=document_type)

    # 6. Parse MRZ & Check digits
    mrz_raw = ocr_res["fields"].get("mrz_raw")
    mrz_res = parse_and_validate_mrz(mrz_raw)

    # If MRZ found fields, supplement any missing visual fields
    if mrz_res["detected"] and mrz_res.get("fields"):
        for k in ["full_name", "document_number", "nationality", "gender"]:
            if not ocr_res["fields"].get(k) and mrz_res["fields"].get(k):
                ocr_res["fields"][k] = mrz_res["fields"][k]

    # 7. Database Matching
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

    # 12. Create Persistent Verification Record in Database
    verification_id = f"IDF-2026-{uuid.uuid4().hex[:5].upper()}"
    matched_doc_id = matching_res.get("matched_record", {}).get("document_id") if matching_res.get("matched_record") else None

    # Face verification eligibility: strictly locked if document is not accepted/verified!
    can_proceed_to_face = (decision == "VERIFIED")

    record = VerificationRecord(
        id=verification_id,
        document_id=matched_doc_id,
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

    return {
        "success": True,
        "verification_id": verification_id,
        "document_id": matched_doc_id,
        "document_type": document_type,
        "image_quality": quality_report,
        "document_status": decision,
        "can_proceed_to_face": can_proceed_to_face,
        "risk_level": risk_res["risk_level"],
        "risk_score": risk_res["risk_score"],
        "risk_reasons": risk_res["reasons"],
        "ocr_result": {
            "fields": ocr_res["fields"],
            "full_text": ocr_res["full_text"],
            "average_confidence": ocr_res["average_confidence"]
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
