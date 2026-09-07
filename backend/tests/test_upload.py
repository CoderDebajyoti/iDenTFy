import io
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_synthetic_passport_image() -> bytes:
    """Generate a clean synthetic passport image with synthetic text."""
    img = Image.new("RGB", (800, 600), color=(245, 247, 250))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (800, 80)], fill=(15, 23, 42))
    d.text((30, 25), "REPUBLIC OF INDIA - PASSPORT", fill=(255, 255, 255))

    # Details
    d.text((50, 120), "SURNAME: SHARMA", fill=(15, 23, 42))
    d.text((50, 160), "GIVEN NAMES: AARAV", fill=(15, 23, 42))
    d.text((50, 200), "NATIONALITY: IND", fill=(15, 23, 42))
    d.text((50, 240), "DATE OF BIRTH: 1995-08-15", fill=(15, 23, 42))
    d.text((50, 280), "PASSPORT NO: Z6549210", fill=(37, 99, 235))
    d.text((50, 320), "EXPIRY DATE: 2030-08-14", fill=(15, 23, 42))

    # Synthetic portrait box
    d.rectangle([(560, 110), (740, 350)], fill=(200, 210, 220), outline=(56, 189, 248), width=2)
    # Head circle
    d.ellipse([(610, 150), (690, 230)], fill=(160, 175, 195))
    # Torso
    d.ellipse([(580, 250), (720, 380)], fill=(120, 140, 165))

    # MRZ lines
    d.rectangle([(20, 460), (780, 560)], fill=(15, 23, 42))
    d.text((40, 480), "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<", fill=(56, 189, 248))
    d.text((40, 515), "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08", fill=(56, 189, 248))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

def test_upload_valid_image():
    img_bytes = create_synthetic_passport_image()
    files = {"document_file": ("passport.jpg", img_bytes, "image/jpeg")}
    data = {"document_type": "passport"}

    response = client.post("/api/v1/document/upload", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "verification_id" in res
    assert "image_quality" in res
    assert res["image_quality"]["valid"] is True
    assert "ocr_result" in res
    assert "document_status" in res

def test_upload_invalid_file_type():
    files = {"document_file": ("test.txt", b"This is not an image", "text/plain")}
    data = {"document_type": "passport"}

    response = client.post("/api/v1/document/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_corrupted_image():
    # Valid JPEG header but corrupted payload
    fake_corrupted = b"\xff\xd8\xff\xe0" + b"corrupted random data" * 5
    files = {"document_file": ("corrupted.jpg", fake_corrupted, "image/jpeg")}
    data = {"document_type": "passport"}

    response = client.post("/api/v1/document/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Failed to decode" in response.json()["detail"]

def test_upload_invalid_document_type():
    img_bytes = create_synthetic_passport_image()
    files = {"document_file": ("passport.jpg", img_bytes, "image/jpeg")}
    data = {"document_type": "spaceship_license"}

    response = client.post("/api/v1/document/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid document_type" in response.json()["detail"]
