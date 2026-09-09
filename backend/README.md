# iDenTFy — AI-Based Fake Identity & Document Screening System (Backend)

High-performance, modular Python backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **OpenCV**, and forensic screening pipelines for border security and identity document verification.

---

## Architecture Pipeline

```
DOCUMENT UPLOAD (multipart/form-data: POST /api/v1/documents/upload)
       │
       ▼
IMAGE PREPROCESSING & QUALITY CHECK
(Resolution, Laplacian Blur, Brightness, Glare, Skew Detection, CLAHE Contrast)
       │
       ▼
OCR EXTRACTION & BOUNDING BOX ANALYSIS (PaddleOCR / Optical Detector)
       │
       ▼
FIELD EXTRACTION (Name, DOB, Doc #, Nationality, Sex, Issue, Expiry, Authority)
       │
       ▼
MRZ PARSING & CHECKSUMS (ICAO Doc 9303 TD1 / TD2 / TD3 7-3-1 Weights)
       │
       ▼
GOVERNMENT PROVIDER ADAPTER ARCHITECTURE
ProviderManager ──► [TestAuthorizedRegistryProvider (Synthetic Sandbox)]
                ──► [ApiSetuProvider (National API Gateway - Configurable)]
                ──► [DigiLockerProvider (DigiLocker Gateway - Configurable)]
       │
       ▼
MATCHING ENGINE (Normalized Exact + Levenshtein / Jaro-Winkler Fuzzy Matching)
       │
       ▼
DOCUMENT VALIDATION ENGINE (Expiry, Internal Consistency, Registry Status)
       │
       ▼
DIGITAL FORENSICS (EXIF Metadata & Error Level Analysis)
       │
       ▼
DOCUMENT DECISION ENGINE (Evidence-based: VERIFIED / REQUIRES_REVIEW / NOT_VERIFIED)
       │
       ├──[If REQUIRES_REVIEW / NOT_VERIFIED] ──► STOP (Face verification strictly blocked with HTTP 403)
       │
       └──[If VERIFIED]
               │
               ▼
       1:1 BIOMETRIC FACE VERIFICATION (OpenCV Face Detection & Cosine Similarity)
               │
               ▼
       FINAL DECISION & RISK ASSESSMENT (0 - 100 Index + Explicit Reasons)
               │
               ▼
       POSTGRESQL AUDIT TRANSACTION PERSISTENCE (verification_records & documents)
```

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI entry point, CORS, global error handlers
│   ├── config.py                # Pydantic Settings and file storage paths
│   ├── api/
│   │   ├── document.py          # POST /api/v1/documents/upload, GET /api/v1/government/providers
│   │   ├── face.py              # POST /api/v1/face/verify (Strictly gated behind VERIFIED)
│   │   └── verification.py      # GET /api/v1/health, history, and dossiers
│   ├── services/
│   │   ├── document_service.py  # End-to-end verification coordinator
│   │   ├── image_preprocessing.py # OpenCV & Pillow preprocessing & optical quality
│   │   ├── ocr_service.py       # PaddleOCR & optical field extraction
│   │   ├── mrz_service.py       # ICAO Doc 9303 check digit validator
│   │   ├── matching_service.py  # Normalized exact & Jaro-Winkler fuzzy matching
│   │   ├── validation_service.py# Expiry, date logic, and registry status
│   │   ├── tampering_service.py # EXIF metadata & Error Level Analysis (ELA)
│   │   ├── decision_service.py  # Evidence-based document decision engine
│   │   ├── risk_service.py      # Transparent weighted risk score
│   │   └── government/          # Government Provider Adapter Architecture
│   │       ├── base_provider.py # GovernmentVerificationProvider abstract interface
│   │       ├── test_provider.py # Isolated TestAuthorizedRegistryProvider (Cases 1-8)
│   │       ├── api_setu_provider.py # API Setu adapter (NOT_CONNECTED when unconfigured)
│   │       ├── digilocker_provider.py # DigiLocker adapter (NOT_CONNECTED when unconfigured)
│   │       └── provider_manager.py # Registry provider lifecycle manager
│   ├── schemas/                 # Pydantic request and response models
│   └── utils/                   # Security, magic bytes, safe paths, image decoders
├── database/
│   ├── database.py              # PostgreSQL SQLAlchemy engine & session factory
│   └── models/                  # Person, Document, Passport, Visa, VerificationRecord
├── uploads/
│   └── temp/                    # Secure temporary storage (non-public, isolated)
└── tests/                       # Automated pytest test suite (44 tests)
```

---

## Setup & Configuration

### 1. Environment Variables (`backend/.env`)

```ini
# PostgreSQL 18 Connection String
DATABASE_URL=postgresql+psycopg2://postgres:MyPostgresPassword123@localhost:5432/fake_identity_screening

# File Upload Settings
UPLOAD_DIR="./uploads"
MAX_UPLOAD_SIZE_BYTES=10485760 # 10 MB

# Biometric Matching Threshold
FACE_SIMILARITY_THRESHOLD=0.68

# Government Registry Provider ('test_registry' for sandbox development)
GOVERNMENT_PROVIDER=test_registry

# Optional: Official Government Credentials (when provisioned)
# API_SETU_CLIENT_ID=""
# API_SETU_API_KEY=""
# DIGILOCKER_CLIENT_ID=""
# DIGILOCKER_CLIENT_SECRET=""
```

### 2. Run Database Initializer & FastAPI Server

```bash
# Activate virtual environment
cd backend
venv\Scripts\activate          # On Windows
# or: source venv/bin/activate # On Linux/macOS

# Run FastAPI Server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI Swagger documentation:
`http://127.0.0.1:8000/docs`

Technical Health Probe:
`GET http://127.0.0.1:8000/api/v1/health`

---

## TEST Registry vs Production Environment

> **Crucial Clarification:**
> "The TEST registry is synthetic and is used only to validate the verification pipeline. Production deployment is designed to integrate with authorized external identity/document verification providers."

- **Production Environment:** PostgreSQL database stores exclusively transactional verification audit records (`verification_records` and `documents`). Production never hardcodes fake citizen data.
- **Isolated TEST Registry (`TestAuthorizedRegistryProvider`):** In-memory synthetic identities covering 8 ground truth scenarios:
  1. Valid matching identity (`Aarav Sharma`, `PA8829104`)
  2. Expired document (`PA1029384`)
  3. Name spelling variation (`ID9918273`)
  4. Date of birth discrepancy (`DL5544332`)
  5. Blacklisted / revoked credential (`PA0099887`)
  6. No registry match (`UNKNOWN999`) -> returns `REQUIRES_REVIEW` (never labeled fake without proof)
  7. Suspended document credential (`ID4433221`)
  8. Valid foreign residence permit (`RP7788990`)

---

## Government API Adapter Architecture

External identity verification is abstracted through `GovernmentVerificationProvider`:
```python
from app.services.government.base_provider import GovernmentVerificationProvider

class CustomGovernmentProvider(GovernmentVerificationProvider):
    # Implement verify_identity, verify_document, get_document_record, get_provider_status
    ...
```

Adding future providers (e.g., API Setu, DigiLocker, UIDAI, CVIS):
1. Subclass `GovernmentVerificationProvider`.
2. Register the provider in `ProviderManager` (`backend/app/services/government/provider_manager.py`).
3. Set `GOVERNMENT_PROVIDER=provider_id` in `.env`.
4. If unconfigured or unauthorized, adapters return `status: "NOT_CONNECTED"` and `"Government verification provider is not configured."` without simulating false responses.

---

## Security Considerations

1. **Secure Storage:** Uploaded files are written only to `uploads/temp/` with cryptographically random UUID filenames.
2. **No Public Static Exposure:** The uploads directory is not mounted as a static route; raw images cannot be downloaded or browsed via HTTP.
3. **No Database Blobs:** Raw images are never stored as PostgreSQL bytea/blobs.
4. **Document-First Gating:** 1:1 Biometric face verification is strictly gated behind `decision == 'VERIFIED'`. Unverified or unreviewed documents return HTTP 403.
5. **Evidence-Based Decisions:** An unindexed document returns `REQUIRES_REVIEW`, not `FAKE`.

---

## Running Automated Tests

```bash
cd backend
venv\Scripts\python.exe -m pytest tests -v
```

All 44 automated tests execute across upload validation, optical preprocessing, OCR, MRZ check digits, government provider routing, tampering forensics, face gating, and PostgreSQL persistence.
