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
       (Blur, Brightness,       (RapidOCR-ONNX /      (ICAO 9303
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
│   ├── tests/                   # 73-test automated pytest verification suite
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

## 🛠️ Running the Application Locally

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
All 73 tests validate upload screening, fuzzy matching, MRZ check digits, tampering forensics, face gating, and decision rules.

---

## ☁️ Live Production Deployment on Render

iDenTFy is designed for seamless, independent deployment on [Render](https://render.com) using a production PostgreSQL database, FastAPI Python web service, and React static site.

### Deployment Architecture & Environment Variables

| Service | Render Type | Root Directory | Build Command | Start Command / Publish Directory | Required Environment Variables |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Database** | Managed PostgreSQL | N/A | Automated by Render | N/A | `DATABASE_URL` (Auto-generated by Render) |
| **Backend** | Web Service (Python 3.12) | `backend` | `pip install -r requirements.txt` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | `DATABASE_URL` (From Postgres)<br>`FRONTEND_URL` (e.g. `https://identfy-frontend.onrender.com`)<br>`DATABASE_MATCHING_ENABLED`=`false`<br>`FACE_SIMILARITY_THRESHOLD`=`0.68`<br>`ENV`=`production`<br>`DEBUG`=`false` |
| **Frontend** | Static Site | `.` (Root) | `npm install && npm run build` | `dist` | `VITE_API_BASE_URL` (e.g. `https://identfy-backend.onrender.com`) |

---

### Step-by-Step Render Setup Guide

#### Step 1: Create Managed PostgreSQL Database
1. In Render Dashboard, click **New +** $\to$ **PostgreSQL**.
2. Name: `identfy-postgres` (Database: `identfy_db`, User: `identfy_user`).
3. Select region (e.g. `Oregon`) and create database.
4. Copy the **Internal Database URL** (or Render will link it automatically).

#### Step 2: Deploy Backend Web Service
1. In Render Dashboard, click **New +** $\to$ **Web Service**.
2. Connect your `iDenTFy` GitHub repository.
3. Configure settings:
   - **Name**: `identfy-backend`
   - **Runtime**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/v1/health`
4. In **Environment Variables**, add:
   - `DATABASE_URL`: Connection string from Step 1
   - `FRONTEND_URL`: URL of your frontend static site (e.g. `https://identfy-frontend.onrender.com`)
   - `DATABASE_MATCHING_ENABLED`: `false`
   - `FACE_SIMILARITY_THRESHOLD`: `0.68`
   - `ENV`: `production`
   - `DEBUG`: `false`

#### Step 3: Deploy Frontend Static Site
1. In Render Dashboard, click **New +** $\to$ **Static Site**.
2. Connect your `iDenTFy` GitHub repository.
3. Configure settings:
   - **Name**: `identfy-frontend`
   - **Root Directory**: `.` (leave empty or set to root)
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. In **Redirects / Rewrites**, add Single Page Application rewrite rule:
   - **Source**: `/*` $\to$ **Destination**: `/index.html` (Action: `Rewrite`)
5. In **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://identfy-backend.onrender.com` (Your backend service URL from Step 2)

---

### Verification Checklist Post-Deployment
- [x] **Backend Health Check**: `GET https://identfy-backend.onrender.com/api/v1/health` returns `200 OK` with `{"status": "healthy", "database": "connected"}`.
- [x] **Swagger API Docs**: `GET https://identfy-backend.onrender.com/docs` opens interactive API specification.
- [x] **Document Screening**: Upload sample passport / ID via frontend UI; check OCR extraction, MRZ status badge, and forensic analysis.
- [x] **Audit History**: Check History view; verifies persistent PostgreSQL storage of screening sessions.
