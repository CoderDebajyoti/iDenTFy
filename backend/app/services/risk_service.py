"""
Risk Assessment Engine
Computes transparent composite fraud risk score (0-100) and risk tier (LOW, MEDIUM, HIGH).
Provides explicit audit reasons for every point added to the risk index.
"""

from typing import Dict, Any, Tuple, List, Optional

def calculate_risk_assessment(
    document_decision: str,
    matching_result: Dict[str, Any],
    ocr_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    tampering_result: Dict[str, Any],
    face_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Weighted rule-based risk calculation:
    - Base score: 10
    - Blacklisted: +90 (Max Risk)
    - Suspended / Tampered: +75
    - Expired: +40
    - Database unindexed: +35
    - Partial name match: +20
    - ELA elevated: +20
    - Low OCR confidence: +15
    - Face verification mismatch: +50
    """
    score = 10
    reasons = []

    # 1. Document Status & Severe Hazards
    if document_decision == "BLACKLISTED":
        score += 85
        reasons.append("Critical Hazard: Document recorded as blacklisted/stolen (+85)")
    elif document_decision == "NOT_VERIFIED":
        score += 70
        reasons.append("Security Alert: Digital tampering or forgery detected (+70)")
    elif document_decision == "SUSPENDED":
        score += 50
        reasons.append("Regulatory Flag: Document suspended by authority (+50)")
    elif document_decision == "EXPIRED":
        score += 35
        reasons.append("Validity Issue: Credential expired (+35)")

    # 2. Database Matching
    match_type = matching_result.get("match_type")
    if match_type == "no_match" or not matching_result.get("database_match"):
        score += 25
        reasons.append("Registry Notice: Credential not indexed in database (+25)")
    elif match_type == "partial_match":
        score += 15
        reasons.append("Identity Notice: Name spelling variation detected (+15)")

    # 3. Tampering Signals
    if tampering_result.get("tampering_detected"):
        score += 25
        reasons.append("Forensics: Micro-structural image alteration (+25)")
    elif tampering_result.get("requires_review"):
        score += 15
        reasons.append("Forensics: Elevated Error Level Analysis (ELA) response (+15)")

    # 4. OCR Quality
    avg_conf = ocr_result.get("average_confidence", 1.0)
    if avg_conf < 0.70 and avg_conf > 0.0:
        score += 10
        reasons.append(f"Optical Quality: Low OCR read confidence ({int(avg_conf * 100)}%) (+10)")

    # 5. Face Verification (if evaluated)
    if face_result:
        face_outcome = face_result.get("outcome")
        if face_outcome == "not_matched":
            score += 50
            reasons.append("Biometric Mismatch: Subject does not match document portrait (+50)")
        elif face_outcome == "requires_review":
            score += 20
            reasons.append("Biometric Warning: Low facial feature similarity score (+20)")

    # Clamp score between 5 and 99
    final_score = int(min(max(score, 5), 99))

    # Determine Tier
    if final_score <= 25:
        risk_level = "LOW"
    elif final_score <= 65:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    if not reasons:
        reasons.append("All automated integrity and registry checks passed cleanly.")

    return {
        "risk_level": risk_level,
        "risk_score": final_score,
        "reasons": reasons
    }
