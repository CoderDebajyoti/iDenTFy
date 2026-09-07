# iDenTFy — AI-Based Fake Identity & Document Screening System

A commercial-grade, AI-powered document verification and identity screening platform built for border security, law enforcement, and verification officers. The system detects forged, altered, suspicious, or inconsistent identity documents through multi-signal optical character recognition (OCR), machine-readable zone (MRZ) checksum validation, central registry database matching, digital tampering heuristics (EXIF & Error Level Analysis), 1:1 biometric facial verification, and automated risk assessment.

---

## 🏛️ System Architecture & Workflow

```
                        OFFICER WORKSTATION (REACT UI)
                                     │
                                     │ 1. UPLOAD REAL FILE (multipart/form-data)
                                     ▼
                        FASTAPI BACKEND ENGINE (:8000)
                                     │
               ┌─────────────────────┼─────────────────────┐
               ▼                     ▼                     ▼
      IMAGE QUALITY CHECK     OCR FIELD EXTRACT      MRZ CHECKSUM
       (Blur, Brightness,       (PaddleOCR /          (ICAO 9303
          Resolution)             Optical)           7-3-1 Weights)
               │                     │                     │
               └─────────────────────┼─────────────────────┘
                                     ▼
                         DATABASE MATCHING ENGINE
                        (Exact + Jaro-Winkler Fuzzy)
                                     │
                                     ▼
                         STATUS & DATE VALIDATION
                       (Active, Expired, Blacklist)
                                     │
                                     ▼
                         TAMPERING FORENSIC ENGINE
                       (EXIF Metadata & ELA Anomaly)
                                     │
                                     ▼
                          DOCUMENT DECISION ENGINE
                                     │
        ┌────────────────────────────┴────────────────────────────┐
        │                                                         │
  [REJECTED / EXPIRED / BLACKLISTED]                      [ACCEPTED / VERIFIED]
        │                                                         │
        ▼                                                         ▼
  STOP PROCESSING                                        BIOMETRIC FACE MATCH
(Face Verification Strictly Blocked)                   (1:1 Cosine Embedding)
                                                                  │
                                                                  ▼
                                                        FINAL DECISION & RISK
                                                        (0-100 Composite Index)
```

---

## 🚀 Key Features

1. **Sequential Verification Gating**: Strict security rule enforced on backend and frontend — face verification cannot be executed if document screening has failed or was rejected.
2. **Transparent & Honest AI**: No fake AI results. If deep model weights are unindexed, the system explicitly reports `model_unavailable` and relies on deterministic forensic signals.
3. **ICAO Doc 9303 Compliance**: Implements mathematical check digit validation using repeating 7-3-1 weights for passports and machine-readable documents.
4. **Fuzzy Identity Matching**: Levenshtein distance and Jaro-Winkler algorithms distinguish harmless name spelling variations from fraudulent identity claims.
5. **Digital Tampering Forensics**: Error Level Analysis (ELA) and EXIF metadata inspection flag spliced portrait blocks and editing software signatures.
6. **1:1 Facial Biometric Verification**: Detects and extracts facial regions, calculates normalized embedding descriptors, and measures vector cosine similarity.
7. **FastAPI & PostgreSQL / SQLite**: Fully typed schemas, CORS-secured endpoints, and persistent audit trail for every screening session.

---

## 📦 Project Structure

```
iDenTFy/
├── backend/                     # Python 3.11+ FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Environment settings & file paths
│   │   ├── api/                 # Versioned API routes (/api/v1)
│   │   │   ├── document.py      # POST /api/v1/document/upload
│   │   │   ├── face.py          # POST /api/v1/face/verify
│   │   │   └── verification.py  # GET /api/v1/health, history, dossier
│   │   ├── services/            # Modular business logic services
│   │   │   ├── document_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── mrz_service.py
│   │   │   ├── matching_service.py
│   │   │   ├── validation_service.py
│   │   │   ├── tampering_service.py
│   │   │   ├── deep_tamper_model.py
│   │   │   ├── face_service.py
│   │   │   ├── decision_service.py
│   │   │   └── risk_service.py
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── utils/               # Image loaders & security helpers
│   ├── database/
│   │   ├── database.py          # SQLAlchemy engine & session factory
│   │   ├── models/              # Person, Document, Passport, Visa, VerificationRecord
│   │   └── seed.py              # Synthetic seed generator covering all 10 scenarios
│   ├── uploads/                 # Storage for scanned documents and face captures
│   ├── tests/                   # 29-test automated pytest verification suite
│   └── requirements.txt
│
├── src/                         # React 19 + Vite frontend
│   ├── components/              # Document, Face, History, Risk, and Common UI
│   ├── context/                 # VerificationContext (API integration)
│   ├── layouts/                 # AppLayout & Navigation
│   ├── pages/                   # Home, Verify, Processing, Results, History, Settings
│   ├── services/                # API client layer (api.js)
│   └── styles/                  # Clean Vanilla CSS design system
│
└── package.json
```

---

## 🛠️ Running the Application

### 1. Start Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
python -c "import sys; sys.path.insert(0, '.'); from database.seed import seed_database; seed_database()"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Root: `http://127.0.0.1:8000`
- Swagger UI Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 2. Start Frontend (React + Vite)
```bash
npm install
npm run dev
```
Frontend will be active at: `http://localhost:5174/` (or `5173`)

### 3. Run Backend Test Suite
```bash
cd backend
pytest tests -v
```
All 29 tests validate upload screening, fuzzy matching, MRZ check digits, tampering forensics, face gating, and decision rules.
