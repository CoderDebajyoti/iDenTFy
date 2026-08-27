import os
# Disable oneDNN/MKLDNN to prevent PIR executor crash on Windows CPU
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper function to open files for upload
def get_upload_file(filename: str):
    path = os.path.join("test_documents", filename)
    with open(path, "rb") as f:
        # Return tuple (filename, content, content_type)
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif filename.endswith(".png"):
            content_type = "image/png"
        else:
            content_type = "text/plain"
        return (filename, f.read(), content_type)

def test_upload_success():
    """
    Test that uploading a valid, clear image returns HTTP 200, 
    quality assessment info, and correct OCR response.
    """
    filename, content, content_type = get_upload_file("clear.jpg")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["document_type"] == "passport"
    
    # Verify image quality details
    quality = json_data["image_quality"]
    assert quality["width"] == 1000
    assert quality["height"] == 800
    assert quality["resolution_status"] == "acceptable"
    assert quality["blur_status"] == "sharp"
    assert quality["brightness_status"] == "acceptable"
    
    # Verify OCR details
    ocr = json_data["ocr"]
    assert "full_text" in ocr
    assert ocr["average_confidence"] > 0.5
    assert len(ocr["text"]) > 0
    # The OCR should detect words like PASSPORT or SMITH
    assert "PASSPORT" in ocr["full_text"] or "SMITH" in ocr["full_text"]

def test_upload_blurry_document():
    """
    Test that a blurry image is recognized as blurry.
    """
    filename, content, content_type = get_upload_file("blurry.jpg")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["image_quality"]["blur_status"] == "blurry"

def test_upload_dark_document():
    """
    Test that a dark image is recognized as too_dark.
    """
    filename, content, content_type = get_upload_file("dark.jpg")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["image_quality"]["brightness_status"] == "too_dark"

def test_upload_bright_document():
    """
    Test that an over-exposed image is recognized as too_bright.
    """
    filename, content, content_type = get_upload_file("bright.jpg")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["image_quality"]["brightness_status"] == "too_bright"

def test_upload_invalid_image():
    """
    Test that a corrupt/invalid image file is rejected with HTTP 400 and code INVALID_IMAGE.
    """
    filename, content, content_type = get_upload_file("invalid.png")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["status"] == "error"
    assert json_data["error_code"] == "INVALID_IMAGE"
    assert "decoded" in json_data["message"]

def test_upload_unsupported_format():
    """
    Test that unsupported MIME type/extension files are rejected with HTTP 415.
    """
    filename, content, content_type = get_upload_file("unsupported.txt")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 415
    assert "Unsupported format" in response.json()["detail"]

def test_upload_oversized_file():
    """
    Test that files exceeding size limits are rejected with HTTP 413.
    """
    filename, content, content_type = get_upload_file("oversized.png")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "passport"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()

def test_upload_invalid_document_type():
    """
    Test that invalid document types are rejected with HTTP 400.
    """
    filename, content, content_type = get_upload_file("clear.jpg")
    files = {"document_file": (filename, content, content_type)}
    data = {"document_type": "invalid_doc_type"}
    
    response = client.post("/api/v1/document/upload", data=data, files=files)
    assert response.status_code == 400
    assert "Invalid document type" in response.json()["detail"]
