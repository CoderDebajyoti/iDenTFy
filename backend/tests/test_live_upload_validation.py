import os
import sys
import io
import uuid
import httpx
from PIL import Image
import numpy as np

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=================================================================")
    print("STARTING LIVE UPLOAD & VALIDATION TESTS AGAINST FASTAPI + POSTGRES")
    print("=================================================================")

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Test Health
        health_res = client.get("/api/v1/health")
        assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
        health_data = health_res.json()
        print(f"[PASS] 1. Backend Health Check: status={health_data['status']}, db={health_data['database']}")

        # 2. Test Missing File
        print("\n--- Testing Missing File ---")
        missing_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"}
        )
        print(f"Status: {missing_res.status_code}, Response: {missing_res.json()}")
        assert missing_res.status_code in [400, 422], f"Expected 400 or 422 for missing file, got {missing_res.status_code}"
        print("[PASS] 2. Missing File rejected as expected.")

        # 3. Test Empty File (0 bytes)
        print("\n--- Testing Empty File (0 bytes) ---")
        empty_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"},
            files={"document_file": ("empty.jpg", b"", "image/jpeg")}
        )
        print(f"Status: {empty_res.status_code}, Response: {empty_res.json()}")
        assert empty_res.status_code == 400
        assert "empty" in empty_res.json()["detail"].lower()
        print("[PASS] 3. Empty File (0 bytes) rejected as expected.")

        # 4. Test Unsupported File Type (e.g. .pdf or .txt)
        print("\n--- Testing Unsupported File Type (.pdf / .txt) ---")
        txt_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"},
            files={"document_file": ("test_doc.pdf", b"This is a PDF file document content.", "application/pdf")}
        )
        print(f"Status: {txt_res.status_code}, Response: {txt_res.json()}")
        assert txt_res.status_code == 400
        assert "unsupported" in txt_res.json()["detail"].lower()
        print("[PASS] 4. Unsupported File Type (.pdf) rejected as expected.")

        # 5. Test Unsupported MIME Type with spoofed extension
        print("\n--- Testing Unsupported MIME / Spoofed Extension ---")
        spoofed_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"},
            files={"document_file": ("spoofed.jpg", b"Not an image at all but named .jpg", "text/plain")}
        )
        print(f"Status: {spoofed_res.status_code}, Response: {spoofed_res.json()}")
        assert spoofed_res.status_code == 400
        print("[PASS] 5. Unsupported MIME / Spoofed extension rejected as expected.")

        # 6. Test Corrupted Image (Magic bytes valid, but corrupted truncated data)
        print("\n--- Testing Corrupted Image File ---")
        corrupt_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 40 # Incomplete JPEG
        corrupt_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"},
            files={"document_file": ("corrupted.jpg", corrupt_bytes, "image/jpeg")}
        )
        print(f"Status: {corrupt_res.status_code}, Response: {corrupt_res.json()}")
        assert corrupt_res.status_code == 400
        assert "corrupt" in corrupt_res.json()["detail"].lower()
        print("[PASS] 6. Corrupted Image rejected as expected.")

        # 7. Test Oversized File (> 10MB)
        print("\n--- Testing Oversized File (> 10MB) ---")
        big_bytes = b"\xff\xd8\xff" + b"A" * (11 * 1024 * 1024)
        big_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"},
            files={"document_file": ("large.jpg", big_bytes, "image/jpeg")}
        )
        print(f"Status: {big_res.status_code}, Response: {big_res.json()}")
        assert big_res.status_code == 413, f"Expected 413, got {big_res.status_code}"
        assert "exceeds" in big_res.json()["detail"].lower()
        print("[PASS] 7. Oversized File (> 10MB) rejected with 413.")

        # 8. Test Real Valid Document Image Upload
        print("\n--- Testing Real Document Image Upload (Valid JPEG) ---")
        # Generate a real valid image with PIL (dimensions 800x600, high contrast document layout)
        img = Image.new("RGB", (800, 600), color=(245, 245, 240))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, 760, 560], outline=(40, 60, 100), width=3)
        draw.rectangle([60, 80, 220, 280], fill=(200, 210, 220), outline=(100, 100, 100), width=2)
        draw.text((250, 90), "IDENTITY DOCUMENT", fill=(10, 20, 40))
        draw.text((250, 140), "PASSPORT", fill=(20, 40, 80))
        draw.text((250, 190), "DOCUMENT NUMBER: PA8829104", fill=(30, 30, 30))
        draw.text((250, 240), "NATIONALITY: IND", fill=(30, 30, 30))

        img_buf = io.BytesIO()
        img.save(img_buf, format="JPEG", quality=92)
        img_bytes = img_buf.getvalue()

        upload_res = client.post(
            "/api/v1/document/upload",
            data={"document_type": "passport"},
            files={"document_file": ("real_test_passport.jpg", img_bytes, "image/jpeg")}
        )
        print(f"Status: {upload_res.status_code}")
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        res_data = upload_res.json()
        print("Response payload:")
        print(f"  success: {res_data.get('success')}")
        print(f"  verification_id: {res_data.get('verification_id')}")
        print(f"  document_id: {res_data.get('document_id')}")
        print(f"  document_status: {res_data.get('document_status')}")
        print(f"  risk_level: {res_data.get('risk_level')}")
        print(f"  image_quality: {res_data.get('image_quality')}")
        print(f"  ocr_result: {res_data.get('ocr_result')}")
        
        verification_id = res_data["verification_id"]
        document_id = res_data["document_id"]
        print(f"[PASS] 8. Real Document Upload succeeded! Verification ID: {verification_id}")

    # 9. Verify PostgreSQL Database Records
    print("\n--- Verifying Database Records in PostgreSQL ---")
    from database.database import SessionLocal
    from database.models import Document, VerificationRecord

    db = SessionLocal()
    try:
        # Check Document table
        doc_record = db.query(Document).filter(Document.id == document_id).first()
        assert doc_record is not None, f"Document record {document_id} not found in PostgreSQL!"
        print(f"Found PostgreSQL Document Record:")
        print(f"  id: {doc_record.id}")
        print(f"  document_type: {doc_record.document_type}")
        print(f"  document_number: {doc_record.document_number}")
        print(f"  issuing_country: {doc_record.issuing_country}")
        print(f"  status: {doc_record.status}")
        print(f"  created_at: {doc_record.created_at}")

        # Check VerificationRecord table
        verif_record = db.query(VerificationRecord).filter(VerificationRecord.id == verification_id).first()
        assert verif_record is not None, f"Verification record {verification_id} not found in PostgreSQL!"
        print(f"\nFound PostgreSQL Verification Record:")
        print(f"  id: {verif_record.id}")
        print(f"  document_id: {verif_record.document_id}")
        print(f"  verification_status: {verif_record.verification_status}")
        print(f"  risk_level: {verif_record.risk_level}")
        print(f"  risk_score: {verif_record.risk_score}")
        print(f"  officer_notes: {verif_record.officer_notes}")
        print(f"  ocr_data fields: {verif_record.ocr_data.get('fields')}")

        print("\n[PASS] 9. PostgreSQL record confirmed with genuine data.")
    finally:
        db.close()

    # 10. Test Backend Unavailable scenario (simulation)
    print("\n--- Testing Backend Unavailable Handling ---")
    try:
        dead_client = httpx.Client(base_url="http://127.0.0.1:9999", timeout=1.0)
        dead_client.get("/api/v1/health")
    except Exception as e:
        print(f"[PASS] 10. Offline backend raises connection error as expected: {type(e).__name__}")

    print("\n=================================================================")
    print("ALL LIVE TESTS COMPLETED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
