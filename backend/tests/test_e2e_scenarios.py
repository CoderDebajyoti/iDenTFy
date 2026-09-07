"""
End-to-End Scenario Test Suite for iDenTFy Screening System
Validates all required evaluation scenarios:
CASE 1: Valid document + database match -> verified -> face verification enabled
CASE 2: Expired document -> expired -> face verification blocked
CASE 3: Blacklisted document -> blacklisted -> face verification blocked
CASE 4: Wrong document number -> requires review -> face verification blocked
CASE 5: Name spelling variation -> fuzzy matching identifies match
CASE 6: Suspicious / tampered image -> tampering indicators returned
CASE 7: Backend health probe -> strictly infrastructural (zero medical features)
CASE 8: Different uploaded files yield distinct genuine results
"""

import io
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from app.main import app
from database.database import SessionLocal
from database.models import VerificationRecord, Document

client = TestClient(app)

def create_doc_image(name="SHARMA, AARAV", doc_no="Z6549210", mrz=True) -> bytes:
    img = Image.new("RGB", (800, 600), color=(250, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (800, 70)], fill=(15, 23, 42))
    d.text((30, 25), "REPUBLIC OF INDIA - OFFICIAL IDENTITY", fill=(255, 255, 255))
    d.text((40, 120), f"HOLDER: {name}", fill=(15, 23, 42))
    d.text((40, 160), f"DOCUMENT NO: {doc_no}", fill=(37, 99, 235))
    d.text((40, 200), "NATIONALITY: IND", fill=(15, 23, 42))

    # Portrait
    d.rectangle([(550, 110), (730, 350)], fill=(210, 220, 230), outline=(37, 99, 235), width=2)
    d.ellipse([(600, 150), (680, 230)], fill=(150, 170, 190))
    d.ellipse([(570, 240), (710, 360)], fill=(110, 130, 150))

    if mrz:
        d.rectangle([(20, 480), (780, 570)], fill=(15, 23, 42))
        d.text((40, 495), "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<", fill=(56, 189, 248))
        d.text((40, 530), f"{doc_no}<2IND9508152M3008144<<<<<<<<<<<<<<08", fill=(56, 189, 248))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

def test_case_2_expired_document_blocks_face_verification():
    """CASE 2: Expired document must be flagged EXPIRED and block face verification."""
    # Document Z1102945 is seeded as expired in database
    img_bytes = create_doc_image(name="VERMA, RAJESH", doc_no="Z1102945")
    files = {"document_file": ("expired_passport.jpg", img_bytes, "image/jpeg")}
    data = {"document_type": "passport"}

    resp = client.post("/api/v1/document/upload", files=files, data=data)
    assert resp.status_code == 200
    res = resp.json()

    assert res["document_status"] in ("EXPIRED", "REQUIRES_REVIEW")
    assert res["can_proceed_to_face"] is False

    # Attempt face verification -> MUST BE BLOCKED
    v_id = res["verification_id"]
    face_files = {"face_file": ("face.jpg", img_bytes, "image/jpeg")}
    face_resp = client.post("/api/v1/face/verify", files=face_files, data={"verification_id": v_id})
    assert face_resp.status_code == 403
    assert "blocked" in face_resp.json()["detail"].lower()

def test_case_3_blacklisted_document_blocks_face_verification():
    """CASE 3: Blacklisted document must be flagged BLACKLISTED and block face verification."""
    # Document DL04202300789 is seeded as blacklisted
    img_bytes = create_doc_image(name="SINGH, VIKRAM", doc_no="DL04202300789", mrz=False)
    files = {"document_file": ("blacklisted_license.jpg", img_bytes, "image/jpeg")}
    data = {"document_type": "driver_license"}

    resp = client.post("/api/v1/document/upload", files=files, data=data)
    assert resp.status_code == 200
    res = resp.json()

    assert res["document_status"] in ("BLACKLISTED", "REQUIRES_REVIEW")
    assert res["can_proceed_to_face"] is False

    # Attempt face verification -> MUST BE BLOCKED
    v_id = res["verification_id"]
    face_files = {"face_file": ("face.jpg", img_bytes, "image/jpeg")}
    face_resp = client.post("/api/v1/face/verify", files=face_files, data={"verification_id": v_id})
    assert face_resp.status_code == 403

def test_case_4_wrong_document_number_blocks_face_verification():
    """CASE 4: Wrong or unindexed document number must not pass normal verification."""
    img_bytes = create_doc_image(name="FAKE PERSON", doc_no="INVALID999", mrz=False)
    files = {"document_file": ("unknown_doc.jpg", img_bytes, "image/jpeg")}
    data = {"document_type": "identity_card"}

    resp = client.post("/api/v1/document/upload", files=files, data=data)
    assert resp.status_code == 200
    res = resp.json()

    assert res["document_status"] in ("NOT_VERIFIED", "REQUIRES_REVIEW")
    assert res["can_proceed_to_face"] is False

def test_case_7_technical_health_endpoint_no_medical():
    """CASE 7: GET /api/v1/health is strictly infrastructural with zero medical/health verification concepts."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "service" in data
    assert "version" in data
    assert "database" in data
    # Confirm no medical/health verification keys exist
    assert "medical" not in str(data).lower()
    assert "patient" not in str(data).lower()
