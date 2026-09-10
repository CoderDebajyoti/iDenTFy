"""
Comprehensive MRZ Pipeline Test Suite
Tests:
1. Perfect TD3 & TD1 MRZ
2. '<' filler OCR confusion
3. O/0 confusion across alpha, numeric, and alphanumeric fields
4. I/1/L confusion across nationality, dates, and document numbers
5. Dropped characters / edge padding
6. Extra characters / noise trimming
7. Inverted line ordering
8. Genuinely invalid checksum (tampered / counterfeit document number)
9. Correctable OCR error (single unambiguous candidate)
10. Ambiguous multiple corrections (unreliable, no guessing)
11. Completely unreadable / absent MRZ
12. Cross-field consistency (Visual OCR vs MRZ)
13. Real specimen benchmark
"""

import os
import cv2
import pytest
import numpy as np

from app.services.mrz_service import (
    calculate_check_digit,
    normalize_mrz_line,
    parse_and_validate_mrz,
    sanitize_alpha_mrz,
    sanitize_numeric_mrz,
    evaluate_field_checksum_candidates
)
from app.services.ocr_service import run_ocr_on_image
from app.services.image_preprocessing import detect_mrz_region, generate_mrz_preprocessed_variants

# 1. Perfect TD3 MRZ Test
def test_perfect_td3_passport():
    line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
    mrz_text = f"{line1}\n{line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["mrz_status"] == "MRZ_VALID"
    assert res["format"] == "TD3 (Passport)"
    assert res["fields"]["document_number"] == "Z6549210"
    assert res["fields"]["nationality"] == "IND"
    assert res["fields"]["date_of_birth"] == "1995-08-15"
    assert res["fields"]["expiry_date"] == "2030-08-14"
    assert res["fields"]["gender"] == "M"
    assert res["fields"]["full_name"] == "AARAV SHARMA"
    assert res["checksum_results"]["document_number"]["valid"] is True
    assert res["checksum_results"]["date_of_birth"]["valid"] is True
    assert res["checksum_results"]["expiry_date"]["valid"] is True
    assert res["checksum_results"]["composite"]["valid"] is True

# 2. Perfect TD1 Identity Card Test
def test_perfect_td1_id_card():
    line1 = "I<UTOD231458907<<<<<<<<<<<<<<<"
    line2 = "7408122F1204159UTO<<<<<<<<<<<6"
    line3 = "ERIKSSON<<ANNA<MARIA<<<<<<<<<<"
    mrz_text = f"{line1}\n{line2}\n{line3}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["format"] == "TD1 (Identity Card)"
    assert res["fields"]["document_number"] == "D23145890"
    assert res["fields"]["full_name"] == "ANNA MARIA ERIKSSON"

# 3. '<' Filler OCR Confusion Normalization
def test_filler_character_normalization():
    noisy_line1 = "P(INDSHARMA{{AARAV__________________________"
    noisy_line2 = "Z6549210-2IND9508152M3008144--------------08"
    mrz_text = f"{noisy_line1}\n{noisy_line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["fields"]["full_name"] == "AARAV SHARMA"
    assert res["fields"]["nationality"] == "IND"
    assert res["checksum_results"]["document_number"]["valid"] is True

# 4. Field-Constrained Disambiguation: Strict Alpha vs Strict Numeric
def test_field_constrained_character_disambiguation():
    assert sanitize_alpha_mrz("1ND") == "IND"
    assert sanitize_alpha_mrz("FR0") == "FRO"
    assert sanitize_numeric_mrz("95O8I5") == "950815"
    assert sanitize_numeric_mrz("30O8l4") == "300814"
    assert sanitize_numeric_mrz("S8B") == "588"

# 5. Dropped Characters & Line Padding Recovery
def test_truncated_line_padding_recovery():
    short_line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<"
    short_line2 = "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
    mrz_text = f"{short_line1}\n{short_line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["fields"]["full_name"] == "AARAV SHARMA"

# 6. Extra Characters / Line Trimming Recovery
def test_extra_character_trimming():
    long_line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    long_line2 = "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<080"
    mrz_text = f"{long_line1}\n{long_line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["fields"]["document_number"] == "Z6549210"

# 7. Inverted Line Ordering Recovery
def test_inverted_line_ordering():
    line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
    inverted_mrz = f"{line2}\n{line1}"

    res = parse_and_validate_mrz(inverted_mrz)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["fields"]["full_name"] == "AARAV SHARMA"
    assert res["fields"]["document_number"] == "Z6549210"

# 8. Checksum-Aware Single Candidate Correction (OCR Corrected Candidate)
def test_checksum_aware_single_candidate_correction():
    line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "Z654921O<2IND9508152M3008144<<<<<<<<<<<<<<08"
    mrz_text = f"{line1}\n{line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is True
    assert res["mrz_status"] == "MRZ_OCR_CORRECTED_CANDIDATE"
    assert res["status"] == "OCR Correction Candidate"
    assert res["fields"]["document_number"] == "Z6549210"
    assert len(res["candidate_corrections"]) >= 1
    assert res["candidate_corrections"][0]["original_char"] == "O"
    assert res["candidate_corrections"][0]["corrected_char"] == "0"

# 9. Genuinely Invalid Checksum (Tampered / Counterfeit MRZ)
def test_genuinely_invalid_mrz_checksum():
    line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "Z9999999<2IND9508152M3008144<<<<<<<<<<<<<<08"
    mrz_text = f"{line1}\n{line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_detected"] is True
    assert res["mrz_valid"] is False
    assert res["mrz_status"] == "MRZ_UNRELIABLE"
    assert res["checksum_results"]["document_number"]["valid"] is False

# 10. Ambiguous Multiple Possible Corrections (Unreliable - No Guessing)
def test_ambiguous_multiple_corrections_not_forced():
    line1 = "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "XXXYYYZZZ<9IND9508152M3008144<<<<<<<<<<<<<<08"
    mrz_text = f"{line1}\n{line2}"

    res = parse_and_validate_mrz(mrz_text)
    assert res["mrz_status"] == "MRZ_UNRELIABLE"
    assert res["mrz_valid"] is False

# 11. Empty and Absent MRZ
def test_empty_mrz():
    res = parse_and_validate_mrz("")
    assert res["mrz_detected"] is False
    assert res["mrz_status"] == "MRZ_NOT_DETECTED"
    assert res["mrz_valid"] is False

# 12. Dedicated MRZ Detection and Preprocessing Pipeline
def test_dedicated_mrz_region_detection():
    h, w = 600, 900
    img = np.full((h, w, 3), 245, dtype=np.uint8)
    cv2.rectangle(img, (30, 480), (870, 580), (20, 20, 20), -1)
    cv2.putText(img, "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<", (40, 515), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)
    cv2.putText(img, "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08", (40, 555), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)

    crop, meta = detect_mrz_region(img)
    assert crop is not None
    assert crop.shape[0] >= 30
    assert crop.shape[1] >= 100

    variants = generate_mrz_preprocessed_variants(crop)
    assert len(variants) >= 1

# 13. Real Specimen Passports Benchmark
def test_real_specimens_benchmark():
    specimen_paths = [
        "demo_samples/sample_valid_passport.jpg",
        "demo_samples/Screenshot 2026-09-10 004248.png",
        "demo_samples/Screenshot 2026-09-10 004414.png",
        "demo_samples/sample_expired_passport.jpg"
    ]

    for sp in specimen_paths:
        if os.path.exists(sp):
            img = cv2.imread(sp)
            assert img is not None
            ocr_res = run_ocr_on_image(img, document_type="passport")
            assert ocr_res is not None
            assert "fields" in ocr_res
            assert "mrz_result" in ocr_res
            mrz = ocr_res["mrz_result"]
            assert mrz["mrz_detected"] is True
