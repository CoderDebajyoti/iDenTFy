import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.validation_service import validate_document_rules
from app.services.mrz_service import parse_and_validate_mrz, calculate_check_digit

def test_mrz_checksum_calculation():
    # Test ICAO 9303 check digit on known valid samples
    # e.g., 'Z6549210' -> 7-3-1 weights
    check = calculate_check_digit("Z6549210")
    assert isinstance(check, int)
    assert 0 <= check <= 9

    # Test full TD3 MRZ validation (Republic of India standard)
    mrz_lines = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<\nZ6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
    res = parse_and_validate_mrz(mrz_lines)
    assert res["detected"] is True
    assert res["format"] == "TD3 (Passport)"
    assert res["valid"] is True
    assert res["fields"]["full_name"] == "AARAV SHARMA"
    assert res["fields"]["document_number"] == "Z6549210"
    assert res["fields"]["nationality"] == "IND"

def test_expired_document_validation():
    extracted = {"expiry_date": "2020-01-01", "issue_date": "2010-01-01"}
    matching = {"matched_record": {"status": "expired"}}
    mrz = {"detected": False}

    res = validate_document_rules(extracted, matching, mrz)
    assert res["is_expired"] is True
    assert res["status_determination"] == "EXPIRED"
    assert any("expired" in issue.lower() for issue in res["issues"])

def test_blacklisted_document_validation():
    extracted = {"expiry_date": "2030-01-01", "issue_date": "2020-01-01"}
    matching = {"matched_record": {"status": "blacklisted"}}
    mrz = {"detected": False}

    res = validate_document_rules(extracted, matching, mrz)
    assert res["is_blacklisted"] is True
    assert res["status_determination"] == "BLACKLISTED"
    assert any("blacklisted" in issue.lower() for issue in res["issues"])

def test_suspended_document_validation():
    extracted = {"expiry_date": "2030-01-01", "issue_date": "2020-01-01"}
    matching = {"matched_record": {"status": "suspended"}}
    mrz = {"detected": False}

    res = validate_document_rules(extracted, matching, mrz)
    assert res["is_suspended"] is True
    assert res["status_determination"] == "SUSPENDED"
