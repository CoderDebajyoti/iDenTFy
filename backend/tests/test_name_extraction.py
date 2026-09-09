"""
Unit and Integration Tests for Name Extraction, Normalization, and MRZ Cross-Checking.
Strictly verifies genuine extraction logic without fake values or hardcoding.
"""

import pytest
from app.services.mrz_service import parse_mrz_name, parse_mrz_td3_line1, parse_and_validate_mrz
from app.services.ocr_service import (
    normalize_name_string,
    is_valid_name_candidate,
    extract_visual_name,
    evaluate_name_consistency,
    extract_fields_and_confidences
)

def test_case_1_simple_surname_and_given_name():
    """Case 1: Standard surname and given name in TD3 MRZ."""
    line1 = "P<FRAROSTOVA<<ELENA<<<<<<<<<<<<<<<<<<<<<<<<<"
    doc_type, country, surname, given_names, full_name = parse_mrz_td3_line1(line1)
    
    assert doc_type == "P"
    assert country == "FRA"
    assert surname == "ROSTOVA"
    assert given_names == "ELENA"
    assert full_name == "ELENA ROSTOVA"

def test_case_2_multiple_given_names():
    """Case 2: Multiple given names separated by '<'."""
    line1 = "P<USADOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<<"
    doc_type, country, surname, given_names, full_name = parse_mrz_td3_line1(line1)
    
    assert country == "USA"
    assert surname == "DOE"
    assert given_names == "JOHN MICHAEL"
    assert full_name == "JOHN MICHAEL DOE"

def test_case_3_multiple_surname_components():
    """Case 3: Multiple surname components separated by '<'."""
    line1 = "P<GBRDE<SILVA<<MARIA<CONCEICAO<<<<<<<<<<<<<<<"
    doc_type, country, surname, given_names, full_name = parse_mrz_td3_line1(line1)
    
    assert country == "GBR"
    assert surname == "DE SILVA"
    assert given_names == "MARIA CONCEICAO"
    assert full_name == "MARIA CONCEICAO DE SILVA"

def test_case_4_mrz_filler_characters_handling():
    """Case 4: MRZ filler '<' characters are cleaned and not treated as part of name."""
    line1 = "P<IND<SHARMA<<AARAV<KUMAR<<<<<<<<<<<<<<<<<<<"
    _, country, surname, given_names, full_name = parse_mrz_td3_line1(line1)
    
    assert country == "IND"
    assert surname == "SHARMA"
    assert given_names == "AARAV KUMAR"
    assert full_name == "AARAV KUMAR SHARMA"
    assert "<" not in full_name

def test_case_5_mrz_given_name_only_no_surname():
    """Case 5: Holder with no surname (starts with '<<')."""
    line1 = "P<IND<<SHRI<KRISHAN<<<<<<<<<<<<<<<<<<<<<<<<<"
    _, country, surname, given_names, full_name = parse_mrz_td3_line1(line1)
    
    assert country == "IND"
    assert surname == ""
    assert given_names == "SHRI KRISHAN"
    assert full_name == "SHRI KRISHAN"

def test_case_6_visual_ocr_spelling_variation_cross_check():
    """Case 6: Visual OCR slight spelling variation compared against MRZ."""
    vis_name = {
        "full_name": "ARAV SHARMA",
        "surname": "SHARMA",
        "given_names": "ARAV",
        "source": "VISUAL_OCR",
        "confidence": 0.92
    }
    mrz_name = {
        "full_name": "AARAV SHARMA",
        "surname": "SHARMA",
        "given_names": "AARAV",
        "source": "MRZ",
        "confidence": 0.98
    }
    consistency = evaluate_name_consistency(vis_name, mrz_name)
    assert consistency["status"] == "POSSIBLE_OCR_VARIATION"
    assert consistency["similarity"] >= 0.80
    assert consistency["visual_name"] == "ARAV SHARMA"
    assert consistency["mrz_name"] == "AARAV SHARMA"

def test_case_7_missing_visual_name_mrz_only():
    """Case 7: Missing visual name, authoritative MRZ present."""
    vis_name = {"full_name": None, "source": "VISUAL_OCR"}
    mrz_name = {"full_name": "CORINNE BERTHIER", "source": "MRZ"}
    consistency = evaluate_name_consistency(vis_name, mrz_name)
    
    assert consistency["status"] == "SINGLE_SOURCE_ONLY"
    assert consistency["source"] == "MRZ"
    assert consistency["mrz_name"] == "CORINNE BERTHIER"

def test_case_8_missing_mrz_visual_only():
    """Case 8: Document without MRZ, extracted via visual inspection zone."""
    vis_name = {"full_name": "CARLOS SANTANA", "source": "VISUAL_OCR"}
    mrz_name = {"full_name": None, "source": "MRZ"}
    consistency = evaluate_name_consistency(vis_name, mrz_name)
    
    assert consistency["status"] == "SINGLE_SOURCE_ONLY"
    assert consistency["source"] == "VISUAL_OCR"
    assert consistency["visual_name"] == "CARLOS SANTANA"

def test_case_9_label_aware_visual_extraction():
    """Case 9: Label-aware visual extraction from OCR text lines with headers."""
    lines = [
        {"text": "REPUBLIC OF FRANCE - PASSPORT", "confidence": 0.95},
        {"text": "SURNAME: ROSTOVA", "confidence": 0.97},
        {"text": "GIVEN NAMES: ELENA", "confidence": 0.96},
        {"text": "PASSPORT NO: PA9821453", "confidence": 0.99}
    ]
    vis_res = extract_visual_name(lines)
    assert vis_res["status"] == "EXTRACTED"
    assert vis_res["surname"] == "ROSTOVA"
    assert vis_res["given_names"] == "ELENA"
    assert vis_res["full_name"] == "ELENA ROSTOVA"

def test_case_10_completely_unreadable_name_returns_none():
    """Case 10: Completely unreadable/missing name returns null and REQUIRES_REVIEW, never fake text."""
    lines = [
        {"text": "12345 67890", "confidence": 0.40},
        {"text": "--- ---", "confidence": 0.30}
    ]
    fields, field_confs = extract_fields_and_confidences("", "passport", lines)
    assert fields["full_name"] is None
    assert fields["name"]["status"] == "REQUIRES_REVIEW"
    assert fields["name"]["full_name"] is None

def test_name_normalization_safety():
    """Verify name normalization strips junk without destructive number substitutions."""
    raw = "   d'Souza,  Jean-Luc <<  "
    norm = normalize_name_string(raw)
    assert norm == "D'SOUZA JEAN-LUC"
    # Ensure human names with O/I are NOT replaced with 0/1
    assert normalize_name_string("OLIVIA SMITH") == "OLIVIA SMITH"
    assert normalize_name_string("IAN BROWN") == "IAN BROWN"
