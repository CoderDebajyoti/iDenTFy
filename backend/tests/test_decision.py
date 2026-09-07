import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.decision_service import evaluate_document_decision
from app.services.risk_service import calculate_risk_assessment

def test_decision_verified_scenario():
    ocr = {"average_confidence": 0.95, "fields": {}}
    matching = {"database_match": True, "match_type": "strong_match", "name_similarity": 0.98}
    validation = {"is_blacklisted": False, "is_suspended": False, "is_expired": False, "is_valid": True}
    mrz = {"detected": True, "valid": True}
    tampering = {"tampering_detected": False, "requires_review": False, "indicators": []}

    decision, reasons = evaluate_document_decision(ocr, matching, validation, mrz, tampering)
    assert decision == "VERIFIED"

    risk = calculate_risk_assessment(decision, matching, ocr, validation, tampering)
    assert risk["risk_level"] == "LOW"
    assert risk["risk_score"] <= 25

def test_decision_expired_scenario():
    ocr = {"average_confidence": 0.90, "fields": {}}
    matching = {"database_match": True, "match_type": "strong_match"}
    validation = {"is_blacklisted": False, "is_suspended": False, "is_expired": True, "is_valid": False}
    mrz = {"detected": True, "valid": True}
    tampering = {"tampering_detected": False, "requires_review": False}

    decision, reasons = evaluate_document_decision(ocr, matching, validation, mrz, tampering)
    assert decision == "EXPIRED"

def test_decision_blacklisted_scenario():
    ocr = {"average_confidence": 0.90, "fields": {}}
    matching = {"database_match": True, "match_type": "strong_match"}
    validation = {"is_blacklisted": True, "is_suspended": False, "is_expired": False}
    mrz = {"detected": True, "valid": True}
    tampering = {"tampering_detected": False, "requires_review": False}

    decision, reasons = evaluate_document_decision(ocr, matching, validation, mrz, tampering)
    assert decision == "BLACKLISTED"

    risk = calculate_risk_assessment(decision, matching, ocr, validation, tampering)
    assert risk["risk_level"] == "HIGH"
    assert risk["risk_score"] >= 80

def test_decision_tampered_scenario():
    ocr = {"average_confidence": 0.85, "fields": {}}
    matching = {"database_match": False, "match_type": "no_match"}
    validation = {"is_blacklisted": False, "is_suspended": False, "is_expired": False}
    mrz = {"detected": False}
    tampering = {"tampering_detected": True, "requires_review": True, "indicators": ["Copy-paste splicing detected"]}

    decision, reasons = evaluate_document_decision(ocr, matching, validation, mrz, tampering)
    assert decision == "NOT_VERIFIED"
