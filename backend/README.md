# iDenTFy — AI-Based Fake Identity & Document Screening System (Backend)

High-performance, modular Python backend built with **FastAPI**, **SQLAlchemy**, **OpenCV**, and forensic screening pipelines for border security and identity document verification.

---

## Architecture Pipeline

```
DOCUMENT UPLOAD (multipart/form-data)
       │
       ▼
IMAGE QUALITY CHECK (Resolution, Laplacian Blur, Brightness)
       │
       ▼
OCR EXTRACTION (PaddleOCR / Optical Bounding-Boxes)
       │
       ▼
MRZ PARSING & CHECKSUM (ICAO 9303 7-3-1 Weight Verification)
       │
       ▼
DATABASE MATCHING (Exact + Levenshtein / Jaro-Winkler Fuzzy Matching)
       │
       ▼
DOCUMENT VALIDATION (Status: Active, Expired, Blacklisted, Suspended)
       │
       ▼
TAMPERING & FORENSIC ANALYSIS (EXIF Software Heuristics & Error Level Analysis)
       │
       ▼
DOCUMENT DECISION ENGINE (Rule-based synthesis: VERIFIED / REQUIRES_REVIEW / NOT_VERIFIED / etc.)
       │
       ├──[If REJECTED / BLOCKED] ──> STOP (Face verification strictly blocked with HTTP 403)
       │
       └──[If ACCEPTED]
               │
               ▼
       1:1 BIOMETRIC FACE VERIFICATION (OpenCV Face Detection & Cosine Similarity)
               │
               ▼
       FINAL DECISION & COMPOSITE RISK ASSESSMENT (0 - 100 Index + Explicit Reasons)
               │
               ▼
       AUDIT DOSSIER & PERSISTENT VERIFICATION RECORD
```

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI entry point, CORS, global error handlers
│   ├── config.py                # Pydantic Settings and file storage paths
│   ├── api/
│   │   ├── document.py          # POST /api/v1/document/upload
│   │   ├── face.py              # POST /api/v1/face/verify (Strictly gated)
│   │   └── verification.py      # GET /api/v1/health, history, and dossiers
│   ├── services/
│   │   ├── document_service.py  # End-to-end verification coordinator
│   │   ├── ocr_service.py       # OCR line, field, and confidence extraction
│   │   ├── mrz_service.py       # ICAO Doc 9303 check digit validator
│   │   ├── matching_service.py  # Jaro-Winkler & Levenshtein matching
│   │   ├── validation_service.py# Expiry, date logic, and registry status
│   │   ├── tampering_service.py # EXIF metadata & Error Level Analysis (ELA)
│   │   ├── deep_tamper_model.py # PyTorch deep tampering model interface
│   │   ├── face_service.py      # Biometric face detection & vector cosine similarity
│   │   ├── decision_service.py  # Multi-signal decision engine
│   │   └── risk_service.py      # Transparent weighted risk score
│   ├── schemas/                 # Pydantic request and response models
│   └── utils/                   # Image loaders and cryptographic filename security
├── database/
│   ├── database.py              # SQLAlchemy engine & session factory
│   ├── models/                  # Person, Document, Passport, Visa, VerificationRecord
│   └── seed.py                  # Synthetic test database generator
├── uploads/                     # Secure uploaded document & face images
├── tests/                       # Complete 29-test pytest verification suite
├── requirements.txt
└── .env.example
```

---

## Quickstart

### 1. Set Up Virtual Environment & Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # On Windows
pip install -r requirements.txt
```

### 2. Seed Synthetic Database
```bash
python -c "import sys; sys.path.insert(0, '.'); from database.seed import seed_database; seed_database()"
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation is available at:
`http://127.0.0.1:8000/docs`

---

## Running Automated Tests
```bash
pytest tests -v
```
All 29 tests execute across upload validation, fuzzy matching, MRZ check digits, tampering forensics, face gating, and decision rules.
