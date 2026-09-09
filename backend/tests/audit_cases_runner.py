"""
Audit Cases Runner
Directly tests and records real decision logic for Cases A through G:
A. Valid synthetic registry match
B. Expired document
C. Name mismatch
D. DOB mismatch
E. Invalid MRZ checksum
F. No registry match
G. Government provider unavailable
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from app.services.matching_service import match_document_against_database
from app.services.validation_service import validate_document_rules
from app.services.decision_service import evaluate_document_decision
from app.services.mrz_service import parse_and_validate_mrz
from app.services.government.provider_manager import get_provider_manager
from app.services.government.base_provider import GovernmentVerificationProvider

def run_all_cases():
    db = SessionLocal()
    mgr = get_provider_manager()
    orig_provider = mgr.get_active_provider()
    results = {}

    def execute(title, extracted_fields, doc_type, mrz_raw=None, provider_override=None):
        if provider_override:
            mgr.set_active_provider(provider_override.provider_id)
        else:
            mgr.set_active_provider(orig_provider.provider_id)

        mrz_res = parse_and_validate_mrz(mrz_raw)
        matching_res = match_document_against_database(db, extracted_fields, doc_type)
        validation_res = validate_document_rules(extracted_fields, matching_res, mrz_res)

        ocr_mock = {
            "status": "success" if extracted_fields.get("document_number") else "failed",
            "confidence": 0.95,
            "fields": extracted_fields
        }
        tampering_mock = {
            "tampering_detected": False,
            "requires_review": False,
            "confidence": 0.0,
            "indicators": ["Clean EXIF", "Uniform compression"]
        }
        decision, reasons = evaluate_document_decision(
            ocr_result=ocr_mock,
            matching_result=matching_res,
            validation_result=validation_res,
            mrz_result=mrz_res,
            tampering_result=tampering_mock
        )

        results[title] = {
            "ocr_result": {k: v for k, v in extracted_fields.items() if v},
            "validation_result": {
                "valid": validation_res.get("valid"),
                "violations": validation_res.get("violations"),
                "status": validation_res.get("checks", {}).get("status")
            },
            "registry_result": {
                "registry_match": matching_res.get("registry_match"),
                "provider_name": matching_res.get("provider_info", {}).get("name"),
                "is_synthetic": matching_res.get("provider_info", {}).get("is_synthetic")
            },
            "matching_result": {
                "match_type": matching_res.get("match_type"),
                "name_similarity": matching_res.get("name_similarity"),
                "field_matches": matching_res.get("field_matches")
            },
            "decision": decision,
            "reasons": reasons
        }

    try:
        # Case A: Valid synthetic registry match (Aarav Sharma PA8829104)
        execute("Case A: Valid Synthetic Registry Match", {
            "document_number": "PA8829104",
            "full_name": "Aarav Sharma",
            "date_of_birth": "1995-08-15",
            "nationality": "IND",
            "expiry_date": "2030-01-09",
            "issue_date": "2020-01-10"
        }, "passport")

        # Case B: Expired document (Priya Patel PA1029384, expired 2022-05-14)
        execute("Case B: Expired Document", {
            "document_number": "PA1029384",
            "full_name": "Priya Patel",
            "date_of_birth": "1992-04-20",
            "nationality": "IND",
            "expiry_date": "2022-05-14",
            "issue_date": "2012-05-15"
        }, "passport")

        # Case C: Name mismatch (Database has Aarav Sharma, doc has Vikram Sharma)
        execute("Case C: Name Mismatch", {
            "document_number": "PA8829104",
            "full_name": "Vikram Sharma",
            "date_of_birth": "1995-08-15",
            "nationality": "IND",
            "expiry_date": "2030-01-09",
            "issue_date": "2020-01-10"
        }, "passport")

        # Case D: DOB mismatch (Database has Vikram Singh DOB 1990-12-25, doc has 1995-01-01)
        execute("Case D: DOB Mismatch", {
            "document_number": "DL5544332",
            "full_name": "Vikram Singh",
            "date_of_birth": "1995-01-01",
            "nationality": "IND",
            "expiry_date": "2039-03-11",
            "issue_date": "2019-03-12"
        }, "driver_license")

        # Case E: Invalid MRZ Checksum
        bad_mrz = "P<INDASTRA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<<\nPA88291090IND9508154M3001092<<<<<<<<<<<<<<<0"
        execute("Case E: Invalid MRZ Checksum", {
            "document_number": "PA8829104",
            "full_name": "Aarav Sharma",
            "date_of_birth": "1995-08-15",
            "nationality": "IND",
            "expiry_date": "2030-01-09",
            "issue_date": "2020-01-10"
        }, "passport", mrz_raw=bad_mrz)

        # Case F: No Registry Match (PA9999999 not in database)
        execute("Case F: No Registry Match", {
            "document_number": "PA9999999",
            "full_name": "Unknown Person",
            "date_of_birth": "1990-01-01",
            "nationality": "IND",
            "expiry_date": "2030-01-01",
            "issue_date": "2020-01-01"
        }, "passport")

        # Case G: Government Provider Unavailable
        class MockUnavailableProvider(GovernmentVerificationProvider):
            @property
            def provider_id(self): return "unavail_test"
            @property
            def provider_name(self): return "Unavailable Mock Provider"
            @property
            def is_synthetic(self): return False
            def get_provider_status(self): return {"status": "NOT_CONNECTED", "name": "Unavailable Mock Provider", "provider_id": "unavail_test", "is_synthetic": False}
            def verify_document(self, doc_no, doc_type): return {"status": "PROVIDER_UNAVAILABLE", "registry_match": False, "error": "Connection refused"}
            def get_document_record(self, doc_no): return None

        unavail = MockUnavailableProvider()
        mgr.register_provider(unavail)

        execute("Case G: Government Provider Unavailable", {
            "document_number": "PA8829104",
            "full_name": "Aarav Sharma",
            "date_of_birth": "1995-08-15",
            "nationality": "IND",
            "expiry_date": "2030-01-09",
            "issue_date": "2020-01-10"
        }, "passport", provider_override=unavail)

    finally:
        mgr.set_active_provider(orig_provider.provider_id)
        db.close()

    import json
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_all_cases()
