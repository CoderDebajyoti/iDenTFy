"""
Test Authorized Registry Provider (Isolated Synthetic Registry)
Provides isolated in-memory test identities with known ground truth for validation and pipeline testing.
STRICT COMPLIANCE:
- Contains strictly fictional/synthetic ground-truth identities.
- Does NOT interact with or pollute the production PostgreSQL database.
- Clearly flags all outputs as is_synthetic=True and is_test=True.
"""

import re
from typing import Dict, Any, Optional, List
from .base_provider import GovernmentVerificationProvider

def _normalize(s: Optional[str]) -> str:
    if not s:
        return ""
    clean = re.sub(r"[^\w\s]", " ", str(s).lower())
    return re.sub(r"\s+", " ", clean).strip()

def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def _jaro_winkler(s1: str, s2: str) -> float:
    s1 = _normalize(s1)
    s2 = _normalize(s2)
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    len1, len2 = len(s1), len(s2)
    match_distance = max(len1, len2) // 2 - 1
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
    if matches == 0:
        return 0.0
    transpositions = 0
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    transpositions //= 2
    jaro = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0
    prefix = 0
    for i in range(min(4, min(len1, len2))):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
    return round(jaro + prefix * 0.1 * (1.0 - jaro), 3)

# ==============================================================================
# Isolated Synthetic Ground Truth Records (Cases 1 - 8)
# ==============================================================================
SYNTHETIC_REGISTRY_DATABASE: Dict[str, Dict[str, Any]] = {
    # Case 1: Valid Matching Identity (Passport)
    "PA8829104": {
        "document_number": "PA8829104",
        "document_type": "passport",
        "full_name": "Aarav Sharma",
        "date_of_birth": "1995-08-15",
        "nationality": "IND",
        "gender": "M",
        "issuing_country": "IND",
        "issuing_authority": "Regional Passport Office Delhi",
        "issue_date": "2020-01-10",
        "expiry_date": "2030-01-09",
        "status": "active",
        "scenario": "Case 1: Valid matching identity",
        "is_synthetic": True
    },
    # Case 2: Expired Document
    "PA1029384": {
        "document_number": "PA1029384",
        "document_type": "passport",
        "full_name": "Priya Patel",
        "date_of_birth": "1992-04-20",
        "nationality": "IND",
        "gender": "F",
        "issuing_country": "IND",
        "issuing_authority": "Regional Passport Office Mumbai",
        "issue_date": "2012-05-15",
        "expiry_date": "2022-05-14",
        "status": "expired",
        "scenario": "Case 2: Expired document",
        "is_synthetic": True
    },
    # Case 3: Name Spelling Variation (Database stores Rohan Verma)
    "ID9918273": {
        "document_number": "ID9918273",
        "document_type": "identity_card",
        "full_name": "Rohan Verma",
        "date_of_birth": "1988-11-03",
        "nationality": "IND",
        "gender": "M",
        "issuing_country": "IND",
        "issuing_authority": "National ID Authority",
        "issue_date": "2018-09-01",
        "expiry_date": "2028-08-31",
        "status": "active",
        "scenario": "Case 3: Name spelling variation test",
        "is_synthetic": True
    },
    # Case 4: DOB Mismatch (Database stores 1990-12-25)
    "DL5544332": {
        "document_number": "DL5544332",
        "document_type": "driver_license",
        "full_name": "Vikram Singh",
        "date_of_birth": "1990-12-25",
        "nationality": "IND",
        "gender": "M",
        "issuing_country": "IND",
        "issuing_authority": "Transport Department Karnataka",
        "issue_date": "2019-03-12",
        "expiry_date": "2039-03-11",
        "status": "active",
        "scenario": "Case 4: Date of birth mismatch test",
        "is_synthetic": True
    },
    # Case 5: Blacklisted / Invalid Credential
    "PA0099887": {
        "document_number": "PA0099887",
        "document_type": "passport",
        "full_name": "Siddharth Malhotra",
        "date_of_birth": "1985-07-19",
        "nationality": "IND",
        "gender": "M",
        "issuing_country": "IND",
        "issuing_authority": "Passport Seva Kendra",
        "issue_date": "2017-02-10",
        "expiry_date": "2027-02-09",
        "status": "blacklisted",
        "scenario": "Case 5: Blacklisted document credential",
        "is_synthetic": True
    },
    # Case 7: Suspended Identity Card
    "ID4433221": {
        "document_number": "ID4433221",
        "document_type": "identity_card",
        "full_name": "Ananya Roy",
        "date_of_birth": "1997-09-14",
        "nationality": "IND",
        "gender": "F",
        "issuing_country": "IND",
        "issuing_authority": "National ID Authority",
        "issue_date": "2021-06-15",
        "expiry_date": "2031-06-14",
        "status": "suspended",
        "scenario": "Case 7: Suspended document credential",
        "is_synthetic": True
    },
    # Case 8: Valid Residence Permit
    "RP7788990": {
        "document_number": "RP7788990",
        "document_type": "residence_permit",
        "full_name": "Carlos Fernandez",
        "date_of_birth": "1983-02-28",
        "nationality": "ESP",
        "gender": "M",
        "issuing_country": "IND",
        "issuing_authority": "Bureau of Immigration",
        "issue_date": "2022-08-01",
        "expiry_date": "2027-07-31",
        "status": "active",
        "scenario": "Case 8: Valid residence permit",
        "is_synthetic": True
    }
}

class TestAuthorizedRegistryProvider(GovernmentVerificationProvider):
    """
    In-memory isolated test provider implementing the GovernmentVerificationProvider interface.
    """

    @property
    def provider_id(self) -> str:
        return "test_registry"

    @property
    def provider_name(self) -> str:
        return "Test Authorized Registry (Synthetic Sandbox)"

    @property
    def is_synthetic(self) -> bool:
        return True

    def get_provider_status(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.provider_name,
            "status": "ACTIVE",
            "is_synthetic": True,
            "record_count": len(SYNTHETIC_REGISTRY_DATABASE),
            "message": "Isolated synthetic registry active for development and verification testing."
        }

    def get_document_record(self, document_number: str) -> Optional[Dict[str, Any]]:
        norm_key = _normalize(document_number).upper().replace(" ", "")
        for doc_no, record in SYNTHETIC_REGISTRY_DATABASE.items():
            if _normalize(doc_no).upper().replace(" ", "") == norm_key:
                return dict(record)
        return None

    def verify_document(self, document_number: str, document_type: str) -> Dict[str, Any]:
        rec = self.get_document_record(document_number)
        if not rec:
            return {
                "registry_match": False,
                "status": "NOT_FOUND",
                "message": "Document not found in test authorized registry.",
                "is_synthetic": True,
                "record": None
            }

        is_type_match = _normalize(rec.get("document_type")) == _normalize(document_type)
        return {
            "registry_match": True,
            "status": rec.get("status", "active").upper(),
            "type_match": is_type_match,
            "is_synthetic": True,
            "record": rec
        }

    def verify_identity(self, extracted_fields: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        doc_num = extracted_fields.get("document_number")
        full_name = extracted_fields.get("full_name")
        dob = extracted_fields.get("date_of_birth")
        nationality = extracted_fields.get("nationality")

        if not doc_num:
            return {
                "registry_match": False,
                "match_type": "no_match",
                "status": "REQUIRES_REVIEW",
                "field_matches": {
                    "document_number": False,
                    "full_name": False,
                    "date_of_birth": False,
                    "nationality": False
                },
                "name_similarity": 0.0,
                "is_synthetic": True,
                "provider_info": self.get_provider_status(),
                "notes": "No document number extracted for registry lookup."
            }

        rec = self.get_document_record(doc_num)
        if not rec:
            # Check if name exists in synthetic DB for similarity check
            highest_sim = 0.0
            if full_name:
                for item in SYNTHETIC_REGISTRY_DATABASE.values():
                    sim = _jaro_winkler(full_name, item["full_name"])
                    if sim > highest_sim:
                        highest_sim = sim

            return {
                "registry_match": False,
                "match_type": "not_verified",
                "status": "REQUIRES_REVIEW",
                "field_matches": {
                    "document_number": False,
                    "full_name": highest_sim >= 0.85,
                    "date_of_birth": False,
                    "nationality": False
                },
                "name_similarity": highest_sim,
                "is_synthetic": True,
                "provider_info": self.get_provider_status(),
                "notes": "Document number not found in security registry. Record unindexed."
            }

        # Compare fields
        db_name = rec.get("full_name", "")
        db_dob = rec.get("date_of_birth", "")
        db_nat = rec.get("nationality", "")

        name_sim = _jaro_winkler(full_name, db_name) if full_name else 0.0
        name_matched = name_sim >= 0.85
        doc_num_matched = True
        dob_matched = (_normalize(dob) == _normalize(db_dob)) if dob else False
        nat_matched = (_normalize(nationality) == _normalize(db_nat)) if nationality else False

        if name_matched and (dob_matched or nat_matched):
            match_type = "exact" if name_sim >= 0.95 else "partial"
            reg_match = True
        elif name_matched or dob_matched:
            match_type = "partial"
            reg_match = True
        else:
            match_type = "mismatch"
            reg_match = False

        status_str = rec.get("status", "active").upper()

        return {
            "registry_match": reg_match,
            "match_type": match_type,
            "status": status_str,
            "field_matches": {
                "document_number": doc_num_matched,
                "full_name": name_matched,
                "date_of_birth": dob_matched,
                "nationality": nat_matched
            },
            "name_similarity": name_sim,
            "matched_record": rec,
            "is_synthetic": True,
            "provider_info": self.get_provider_status(),
            "notes": f"Matched in synthetic registry. Scenario: {rec.get('scenario')}. Name similarity {int(name_sim * 100)}%."
        }
