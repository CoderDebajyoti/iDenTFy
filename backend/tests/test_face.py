import io
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from database.database import SessionLocal
from database.models import VerificationRecord
from app.services.face_service import calculate_cosine_similarity, extract_face_embedding

client = TestClient(app)

def test_cosine_similarity_math():
    # Identical vectors -> 1.0
    v1 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    assert calculate_cosine_similarity(v1, v1) == 1.0

    # Orthogonal vectors -> 0.0
    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    v3 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    assert calculate_cosine_similarity(v2, v3) == 0.0

def test_face_verification_blocked_on_unverified_document():
    # Attempting to call POST /api/v1/face/verify on a document that is REQUIRES_REVIEW or NOT_VERIFIED
    # must be strictly blocked with HTTP 403 Forbidden!
    img = Image.new("RGB", (200, 200), color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    files = {"face_file": ("face.jpg", buf.getvalue(), "image/jpeg")}
    data = {"verification_id": "IDF-2026-8892B"} # Status is REQUIRES_REVIEW

    response = client.post("/api/v1/face/verify", files=files, data=data)
    assert response.status_code == 403
    assert "blocked" in response.json()["detail"].lower()

def test_face_verification_nonexistent_record():
    img = Image.new("RGB", (200, 200), color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    files = {"face_file": ("face.jpg", buf.getvalue(), "image/jpeg")}
    data = {"verification_id": "NONEXISTENT-RECORD"}

    response = client.post("/api/v1/face/verify", files=files, data=data)
    assert response.status_code == 404
