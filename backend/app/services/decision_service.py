"""
Rule-Based Document Decision Engine
Multi-signal deterministic decision logic combining:
- Document status from registry (Blacklisted, Suspended, Expired)
- Date validation & expiration
- Database/Government provider matching tier (Strong Match, Exact, Partial Match, Unindexed)
- OCR extraction confidence & required fields
- MRZ checksums
- Tampering forensic indicators
"""

from typing import Dict, Any, Tuple, List

def evaluate_document_decision(
    ocr_result: Dict[str, Any],
    matching_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    mrz_result: Dict[str, Any],
    tampering_result: Dict[str, Any]
) -> Tuple[str, List[str]]:
    """
    Synthesize all forensic and registry signals into an actionable document determination.
    Returns:
    - decision: VERIFIED | REQUIRES_REVIEW | NOT_VERIFIED | EXPIRED | BLACKLISTED | SUSPENDED
    - reasons: list of explanation strings
    """
    reasons = []

    # 1. Hard Security Overrides
    if validation_result.get("is_blacklisted"):
        reasons.append("Document explicitly blacklisted in security registry.")
        return "BLACKLISTED", reasons

    if validation_result.get("is_suspended"):
        reasons.append("Document administrative validity currently suspended.")
        return "SUSPENDED", reasons

    if validation_result.get("is_expired"):
        reasons.append("Document expiration date has passed.")
        return "EXPIRED", reasons

    # 2. Critical Validation / Checksum Failures (NOT_VERIFIED)
    mrz_detected = mrz_result.get("mrz_detected", mrz_result.get("detected", False))
    mrz_valid = mrz_result.get("mrz_valid", mrz_result.get("valid", True))
    if mrz_detected and not mrz_valid:
        reasons.append("MRZ check digit checksum mismatch: Cryptographic/checksum verification failed.")
        return "NOT_VERIFIED", reasons

    # 3. Tampering & Forgery Detection (NOT_VERIFIED)
    if tampering_result.get("tampering_detected"):
        reasons.extend(tampering_result.get("indicators", []))
        reasons.append("High probability of digital alteration or forensic manipulation.")
        return "NOT_VERIFIED", reasons

    # 4. Database Matching & Registry Cross-Check
    db_match = matching_result.get("database_match") or matching_result.get("registry_match")
    match_type = matching_result.get("match_type")
    name_sim = matching_result.get("name_similarity", 0.0)

    # 5. Synthesis Rules
    if db_match and match_type in ("strong_match", "exact") and mrz_valid and not tampering_result.get("requires_review"):
        reasons.append("Strong registry match, valid credentials, and clean forensic integrity.")
        return "VERIFIED", reasons

    if match_type == "partial_match" or (0.80 <= name_sim < 0.95):
        reasons.append(f"Name spelling variation or minor field discrepancy (Similarity: {int(name_sim * 100)}%).")
        return "REQUIRES_REVIEW", reasons

    if tampering_result.get("requires_review"):
        reasons.extend(tampering_result.get("indicators", []))
        return "REQUIRES_REVIEW", reasons

    if not db_match:
        reasons.append("Document not found in central registry (unindexed or foreign credential).")
        return "REQUIRES_REVIEW", reasons

    # Fallback to REQUIRES_REVIEW if uncertain
    reasons.append("Automated screening recommends physical manual inspection by officer.")
    return "REQUIRES_REVIEW", reasons
