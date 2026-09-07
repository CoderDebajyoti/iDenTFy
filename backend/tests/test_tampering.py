import io
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image
import numpy as np
from app.services.tampering_service import compute_error_level_analysis, analyze_metadata_forensics
from app.services.deep_tamper_model import advanced_tamper_engine

def test_error_level_analysis():
    # Create test JPEG
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    img_bytes = buf.getvalue()

    ela_res = compute_error_level_analysis(img_bytes)
    assert "mean_error" in ela_res
    assert "std_error" in ela_res
    assert "is_elevated" in ela_res
    assert isinstance(ela_res["mean_error"], float)

def test_metadata_forensics():
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = analyze_metadata_forensics(buf.getvalue())
    assert "has_exif" in res
    assert "is_suspicious" in res

def test_advanced_tampering_model_unavailable_reporting():
    # Must report explicitly that advanced model is unavailable without fake confidence
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    res = advanced_tamper_engine.predict(dummy_img)
    assert res["available"] is False
    assert "unavailable" in res["status"].lower()
    assert res["confidence"] is None
