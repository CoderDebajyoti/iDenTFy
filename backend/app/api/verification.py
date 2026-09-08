from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import get_db
from database.models import VerificationRecord, Document, Person

router = APIRouter(tags=["Verification Dossier & Health"])

@router.get(
    "/health",
    summary="Technical API Infrastructure Health Check",
    description="Technical ping checking FastAPI and database responsiveness. (Strictly infrastructural; not a user-facing health or medical screening feature)."
)
def system_health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(VerificationRecord.__table__.select().limit(1))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "iDenTFy Screening API",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get(
    "/verification/history",
    summary="Retrieve screening audit history",
    description="Returns filterable, paginated audit records of all previous document screenings."
)
@router.get("/verifications", include_in_schema=False)
def get_verification_history(
    q: Optional[str] = Query(None, description="Search term for ID, name, or doc #"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by verification status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(VerificationRecord).order_by(desc(VerificationRecord.created_at))

    if status and status != "all":
        query = query.filter(VerificationRecord.verification_status.ilike(f"%{status}%"))

    if risk_level and risk_level != "all":
        query = query.filter(VerificationRecord.risk_level.ilike(f"%{risk_level}%"))

    records = query.offset(offset).limit(limit).all()

    items = []
    for r in records:
        ocr_f = r.ocr_data.get("fields", {}) if r.ocr_data else {}
        holder = ocr_f.get("full_name") or (r.document.person.full_name if r.document and r.document.person else "Unextracted")
        doc_num = ocr_f.get("document_number") or (r.document.document_number if r.document else "Unextracted")
        doc_type_raw = ocr_f.get("document_type") or (r.document.document_type if r.document else "Document")
        doc_type = doc_type_raw.title().replace("_", " ")
        nationality = ocr_f.get("nationality") or (r.document.issuing_country if r.document else "Not Available")

        # In-memory search filter if q is provided
        if q:
            term = q.lower()
            if term not in r.id.lower() and term not in holder.lower() and term not in doc_num.lower():
                continue

        # Document type filter
        if document_type and document_type != "all":
            if document_type.lower() not in doc_type.lower():
                continue

        status_formatted = r.verification_status.title().replace("_", " ")
        risk_level_formatted = r.risk_level.title() if r.risk_level else "Pending"
        decision_formatted = (r.final_decision or r.verification_status).title().replace("_", " ")

        items.append({
            "id": r.id,
            "timestamp": r.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "document_type": doc_type,
            "documentType": doc_type,
            "holder_name": holder,
            "holderName": holder,
            "document_number": doc_num,
            "documentNumber": doc_num,
            "nationality": nationality,
            "status": status_formatted,
            "risk_level": risk_level_formatted,
            "riskLevel": risk_level_formatted,
            "risk_score": r.risk_score,
            "riskScore": r.risk_score,
            "final_decision": decision_formatted,
            "finalDecision": decision_formatted
        })

    return items

@router.get(
    "/verification/{verification_id}",
    summary="Retrieve complete forensic dossier",
    description="Returns full structured audit details for an individual verification record."
)
@router.get("/verifications/{verification_id}", include_in_schema=False)
def get_verification_dossier(verification_id: str, db: Session = Depends(get_db)):
    record = db.query(VerificationRecord).filter(VerificationRecord.id == verification_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification dossier '{verification_id}' not found."
        )

    ocr_f = record.ocr_data.get("fields", {}) if record.ocr_data else {}
    holder = ocr_f.get("full_name") or (record.document.person.full_name if record.document and record.document.person else "Unextracted")
    doc_num = ocr_f.get("document_number") or (record.document.document_number if record.document else "Unextracted")
    doc_type_raw = ocr_f.get("document_type") or (record.document.document_type if record.document else "Document")
    doc_type = doc_type_raw.title().replace("_", " ")
    nationality = ocr_f.get("nationality") or (record.document.issuing_country if record.document else "Not Available")

    status_formatted = record.verification_status.title().replace("_", " ")
    risk_level_formatted = record.risk_level.title() if record.risk_level else "Pending"
    decision_formatted = (record.final_decision or record.verification_status).title().replace("_", " ")

    db_match_str = "No Match"
    if record.matching_data:
        db_match_str = record.matching_data.get("match_type", "no_match").title().replace("_", " ")

    tamper_str = "No Anomalies Detected"
    if record.tampering_data:
        if record.tampering_data.get("tampering_detected"):
            tamper_str = "Anomalies Found"
        elif record.tampering_data.get("requires_review"):
            tamper_str = "Review Recommended"

    face_str = "Pending"
    if record.face_data:
        face_str = record.face_data.get("outcome", "Pending").title().replace("_", " ")

    # Real tampering metrics only
    tamper_data = record.tampering_data or {}
    tamper_indicators = tamper_data.get("indicators", [])
    tamper_summary = "; ".join(tamper_indicators) if tamper_indicators else "No tampering indicators detected"

    image_integrity_val = "Passed"
    if tamper_data.get("tampering_detected"):
        image_integrity_val = "Failed (Manipulation Found)"
    elif tamper_data.get("requires_review"):
        image_integrity_val = "Requires Review (Elevated Anomaly)"

    return {
        "id": record.id,
        "timestamp": record.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "document_type": doc_type,
        "documentType": doc_type,
        "holder_name": holder,
        "holderName": holder,
        "document_number": doc_num,
        "documentNumber": doc_num,
        "nationality": nationality,
        "status": status_formatted,
        "risk_level": risk_level_formatted,
        "riskLevel": risk_level_formatted,
        "risk_score": record.risk_score,
        "riskScore": record.risk_score,
        "document_status": record.document_decision or record.verification_status,
        "documentStatus": record.document_decision or record.verification_status,
        "database_match": db_match_str,
        "databaseMatch": db_match_str,
        "tamper_detection": tamper_str,
        "tamperDetection": tamper_str,
        "face_verification": face_str,
        "faceVerification": face_str,
        "final_decision": decision_formatted,
        "finalDecision": decision_formatted,
        "officer_notes": record.officer_notes or "Screening processed per standard protocol.",
        "officerNotes": record.officer_notes or "Screening processed per standard protocol.",
        "ocr_details": {
            "fullName": ocr_f.get("full_name") or "Not Available",
            "documentNumber": ocr_f.get("document_number") or "Not Available",
            "dob": ocr_f.get("date_of_birth") or "Not Available",
            "nationality": ocr_f.get("nationality") or "Not Available",
            "documentType": doc_type,
            "issueDate": ocr_f.get("issue_date") or "Not Available",
            "expiryDate": ocr_f.get("expiry_date") or "Not Available",
            "mrzRaw": ocr_f.get("mrz_raw")
        },
        "ocrDetails": {
            "fullName": ocr_f.get("full_name") or "Not Available",
            "documentNumber": ocr_f.get("document_number") or "Not Available",
            "dob": ocr_f.get("date_of_birth") or "Not Available",
            "nationality": ocr_f.get("nationality") or "Not Available",
            "documentType": doc_type,
            "issueDate": ocr_f.get("issue_date") or "Not Available",
            "expiryDate": ocr_f.get("expiry_date") or "Not Available",
            "mrzRaw": ocr_f.get("mrz_raw")
        },
        "tamper_forensics": {
            "image_integrity": image_integrity_val,
            "imageIntegrity": image_integrity_val,
            "metadata_analysis": tamper_data.get("metadata_analysis", {}).get("summary", "Not Available"),
            "metadataAnalysis": tamper_data.get("metadata_analysis", {}).get("summary", "Not Available"),
            "tampering_indicators": tamper_summary,
            "tamperingIndicators": tamper_summary
        },
        "tamperForensics": {
            "image_integrity": image_integrity_val,
            "imageIntegrity": image_integrity_val,
            "metadata_analysis": tamper_data.get("metadata_analysis", {}).get("summary", "Not Available"),
            "metadataAnalysis": tamper_data.get("metadata_analysis", {}).get("summary", "Not Available"),
            "tampering_indicators": tamper_summary,
            "tamperingIndicators": tamper_summary
        }
    }
