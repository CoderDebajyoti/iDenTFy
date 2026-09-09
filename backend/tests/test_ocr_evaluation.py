"""
OCR Quality & Accuracy Evaluation Tests
Evaluates multi-stage preprocessing, multi-pass OCR, field extraction accuracy,
MRZ check-digit verification, and latency across real document specimens.
"""

import os
import cv2
import pytest
from app.services.image_preprocessing import preprocess_document_for_ocr, assess_optical_quality
from app.services.ocr_service import run_ocr_on_image
from app.services.mrz_service import parse_and_validate_mrz

DEMO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "demo_samples")

def test_ocr_specimen_shri_krishan_passport():
    img_path = os.path.join(DEMO_DIR, "Screenshot 2026-09-10 004248.png")
    if not os.path.exists(img_path):
        pytest.skip(f"Test specimen {img_path} not found")

    img = cv2.imread(img_path)
    assert img is not None

    enhanced_img, prep_meta = preprocess_document_for_ocr(img)
    assert "quality" in prep_meta
    assert "quality_rating" in prep_meta["quality"]

    ocr_res = run_ocr_on_image(enhanced_img, document_type="passport")
    assert ocr_res["status"] == "success"
    assert ocr_res["quality_score"] in ["GOOD", "FAIR"]

    fields = ocr_res["fields"]
    # Check document number correctly extracted
    assert fields["document_number"] == "K9096335"
    assert fields["nationality"] == "IND"
    assert fields["mrz_raw"] is not None

    mrz_res = parse_and_validate_mrz(fields["mrz_raw"])
    assert mrz_res["detected"] is True
    assert mrz_res["checksum_results"]["document_number"]["valid"] is True
    assert mrz_res["fields"]["document_number"] == "K9096335"

def test_ocr_specimen_aman_jilani_passport():
    img_path = os.path.join(DEMO_DIR, "Screenshot 2026-09-10 004414.png")
    if not os.path.exists(img_path):
        pytest.skip(f"Test specimen {img_path} not found")

    img = cv2.imread(img_path)
    assert img is not None

    enhanced_img, prep_meta = preprocess_document_for_ocr(img)
    ocr_res = run_ocr_on_image(enhanced_img, document_type="passport")
    assert ocr_res["status"] == "success"

    fields = ocr_res["fields"]
    assert fields["document_number"] == "X6338455"
    assert fields["nationality"] == "IND"

    mrz_res = parse_and_validate_mrz(fields["mrz_raw"])
    assert mrz_res["detected"] is True
    assert mrz_res["valid"] is True

def test_ocr_specimen_valid_french_passport():
    img_path = os.path.join(DEMO_DIR, "sample_valid_passport.jpg")
    if not os.path.exists(img_path):
        pytest.skip(f"Test specimen {img_path} not found")

    img = cv2.imread(img_path)
    assert img is not None

    enhanced_img, prep_meta = preprocess_document_for_ocr(img)
    ocr_res = run_ocr_on_image(enhanced_img, document_type="passport")

    fields = ocr_res["fields"]
    assert fields["document_number"] == "PA9821453"
    assert fields["nationality"] == "FRA"

def test_ocr_field_level_confidence():
    img_path = os.path.join(DEMO_DIR, "sample_valid_passport.jpg")
    if not os.path.exists(img_path):
        pytest.skip(f"Test specimen {img_path} not found")

    img = cv2.imread(img_path)
    enhanced_img, _ = preprocess_document_for_ocr(img)
    ocr_res = run_ocr_on_image(enhanced_img, document_type="passport")

    assert "field_confidence" in ocr_res
    fc = ocr_res["field_confidence"]
    assert isinstance(fc, dict)
    assert "document_number" in fc
    assert "quality_score" in ocr_res
    assert ocr_res["quality_score"] in ["GOOD", "FAIR", "POOR"]
