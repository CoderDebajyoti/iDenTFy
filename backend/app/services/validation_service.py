"""
Document Validation Service
Validates:
- Expiry date (checks against current date; expired is NOT called forged, but 'EXPIRED')
- Issue date (cannot be in the future)
- Date consistency (issue_date < expiry_date)
- Document registry status (active, expired, blacklisted, suspended)
- Field consistency between visual zone and MRZ
"""

from datetime import datetime, date
from typing import Dict, Any, Optional

def parse_iso_or_custom_date(d_str: Optional[str]) -> Optional[date]:
    """Safely parse various date string formats."""
    if not d_str:
        return None
    d_clean = d_str.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%y%m%d"):
        try:
            return datetime.strptime(d_clean, fmt).date()
        except ValueError:
            continue
    return None

def validate_document_rules(
    extracted_fields: Dict[str, Any],
    matching_result: Dict[str, Any],
    mrz_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate status, dates, and cross-zone consistency.
    """
    today = date.today()
    issues = []
    status_override = None

    matched_record = matching_result.get("matched_record")

    # 1. Check Document Registry Status if record was found
    if matched_record:
        reg_status = str(matched_record.get("status", "")).lower()
        if reg_status == "blacklisted":
            status_override = "BLACKLISTED"
            issues.append("SECURITY ALERT: Document is flagged as BLACKLISTED/STOLEN in central registry.")
        elif reg_status == "suspended":
            status_override = "SUSPENDED"
            issues.append("Document is currently SUSPENDED pending judicial/administrative review.")
        elif reg_status == "expired":
            status_override = "EXPIRED"
            issues.append("Document has expired per official registry records.")
    else:
        # Record not in database
        issues.append("Document not found in central database. Requires secondary verification.")

    # 2. Date Expiry and Issue validation
    expiry_str = extracted_fields.get("expiry_date")
    issue_str = extracted_fields.get("issue_date")

    # Fallback to matched record dates if OCR missed them
    if not expiry_str and matched_record:
        expiry_str = matched_record.get("expiry_date")
    if not issue_str and matched_record:
        issue_str = matched_record.get("issue_date")

    parsed_expiry = parse_iso_or_custom_date(expiry_str)
    parsed_issue = parse_iso_or_custom_date(issue_str)

    is_expired = False
    if parsed_expiry:
        if parsed_expiry < today:
            is_expired = True
            if not status_override:
                status_override = "EXPIRED"
            issues.append(f"Document expired on {parsed_expiry.isoformat()}. Not valid for travel or verification.")

    if parsed_issue and parsed_issue > today:
        issues.append(f"Inconsistent issue date: Date {parsed_issue.isoformat()} is in the future.")

    if parsed_issue and parsed_expiry and parsed_expiry <= parsed_issue:
        issues.append("Date inconsistency: Expiration date cannot precede or equal issue date.")

    # 3. MRZ vs Visual Zone Consistency
    mrz_fields = mrz_result.get("fields", {})
    if mrz_result.get("detected") and mrz_fields:
        mrz_doc_num = mrz_fields.get("document_number")
        vis_doc_num = extracted_fields.get("document_number")
        if mrz_doc_num and vis_doc_num:
            if mrz_doc_num.upper() != vis_doc_num.upper():
                issues.append(f"Cross-field inconsistency: Visual doc # ({vis_doc_num}) does not match MRZ doc # ({mrz_doc_num}).")

    # Determine general validity
    is_valid = (len(issues) == 0) and (status_override is None)

    return {
        "is_valid": is_valid,
        "status_determination": status_override or ("VALID" if is_valid else "REQUIRES_REVIEW"),
        "is_expired": is_expired or (status_override == "EXPIRED"),
        "is_blacklisted": status_override == "BLACKLISTED",
        "is_suspended": status_override == "SUSPENDED",
        "issues": issues,
        "dates_checked": {
            "issue_date": parsed_issue.isoformat() if parsed_issue else None,
            "expiry_date": parsed_expiry.isoformat() if parsed_expiry else None,
            "current_date": today.isoformat()
        }
    }
