from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    """
    Test GET /api/v1/health returns success and correct schema.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "identity-document-screening-backend"
    assert "version" in json_data
    assert json_data["version"] == "0.1.0"

def test_document_status():
    """
    Test GET /api/v1/document/status returns the correct placeholder info.
    """
    response = client.get("/api/v1/document/status")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["module"] == "document-verification"
    assert json_data["status"] == "not_implemented"
    assert json_data["phase"] == 1

def test_face_status():
    """
    Test GET /api/v1/face/status returns the correct placeholder info.
    """
    response = client.get("/api/v1/face/status")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["module"] == "face-verification"
    assert json_data["status"] == "not_implemented"
    assert json_data["phase"] == 1
