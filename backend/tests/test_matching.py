import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.matching_service import (
    normalize_string,
    levenshtein_distance,
    jaro_winkler_similarity,
    match_document_against_database
)
from database.database import SessionLocal

def test_string_normalization():
    assert normalize_string("  Aarav   SHARMA!! ") == "aarav sharma"
    assert normalize_string("Debajyoti-Das") == "debajyoti das"
    assert normalize_string(None) == ""

def test_fuzzy_name_matching():
    # Debajyoti Das vs Debojyoti Das
    sim1 = jaro_winkler_similarity("Debajyoti Das", "Debojyoti Das")
    assert sim1 > 0.90 # High similarity

    # Priya Patel vs Priyaa Patel (spelling variation)
    sim2 = jaro_winkler_similarity("Priya Patel", "Priyaa Patel")
    assert sim2 > 0.90

    # Completely different names
    sim3 = jaro_winkler_similarity("Aarav Sharma", "Vikram Singh")
    assert sim3 < 0.60

    # Levenshtein distance
    dist = levenshtein_distance("Aarav", "Arav")
    assert dist == 1

def test_database_exact_match():
    db = SessionLocal()
    try:
        fields = {
            "document_number": "Z6549210",
            "full_name": "Aarav Sharma",
            "date_of_birth": "1995-08-15",
            "nationality": "IND"
        }
        res = match_document_against_database(db, fields, "passport")
        assert res["database_match"] is True
        assert res["match_type"] == "strong_match"
        assert res["field_matches"]["document_number"] is True
        assert res["field_matches"]["name"] is True
        assert res["name_similarity"] >= 0.95
    finally:
        db.close()

def test_database_spelling_variation_match():
    db = SessionLocal()
    try:
        fields = {
            "document_number": "ID5502914",
            "full_name": "Priyaa Patel", # Spelling variation of Priya Patel
            "date_of_birth": "1991-11-23",
            "nationality": "IND"
        }
        res = match_document_against_database(db, fields, "identity_card")
        assert res["database_match"] is True
        assert res["name_similarity"] >= 0.85
    finally:
        db.close()

def test_database_unindexed_document():
    db = SessionLocal()
    try:
        fields = {
            "document_number": "NONEXISTENT999",
            "full_name": "Unknown Person",
            "date_of_birth": "1990-01-01",
            "nationality": "USA"
        }
        res = match_document_against_database(db, fields, "passport")
        assert res["database_match"] is False
        assert res["match_type"] == "not_verified"
    finally:
        db.close()
