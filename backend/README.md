# AI-Based Fake Identity & Document Screening System - Backend

## Current Phase
**Phase 2 — Document Upload + OCR Backend**

## Capabilities
In this phase (Phase 2), the following pipeline is implemented:
- **Document upload** via REST API (`POST /api/v1/document/upload`).
- **File validation** verifying sizes (< 10MB), extension types (.jpg, .jpeg, .png), MIME types, and header verification.
- **Image quality assessment** checking resolution (minimum dimensions 800x600), blur metric using Laplacian variance, and brightness metric using grayscale mean values.
- **Basic image preprocessing** including edge-preserving bilateral denoising and CLAHE contrast enhancement in LAB space.
- **PaddleOCR integration** loading models once, running predictions, and compiling bounding box coords, text contents, and confidence metrics.

---

## Technical Architecture Status

```text
Done:
✓ FastAPI backend foundation (Phase 1)
✓ Document upload & file validations (Phase 2)
✓ Image quality checks (resolution, blur, brightness) (Phase 2)
✓ Bilateral denoising & contrast preprocessing (Phase 2)
✓ PaddleOCR text extraction (Phase 2)
✓ OCR confidence and bounding box coordinate mapping (Phase 2)

Not implemented yet:
- MRZ extraction and parsing
- MRZ checksum validation
- Field-level document validations (e.g. Names, DOBs, Expiry)
- Fuzzy matching
- Tampering detection (forensics, metadata, ELA)
- Face verification
- Risk scoring engine
- Database integration (PostgreSQL)

Health Verification:
- User-facing Health Verification / Screening has been REMOVED from the project scope.
- Note: The technical endpoint `GET /api/v1/health` is strictly a server liveness/monitoring health check, NOT medical screening.
```

---

## Setup & Installation

Follow these steps from the `backend/` directory to get started:

### 1. Create a Python Virtual Environment
Create a virtual environment named `.venv`:
```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment
On Windows (PowerShell/CMD):
```powershell
.venv\Scripts\activate
```

On macOS/Linux:
```bash
source .venv/bin/activate
```

### 3. Install Dependencies
Install the required packages:
```powershell
pip install -r requirements.txt
```

---

## Running the Server

Start the FastAPI application in development mode with auto-reload:
```powershell
uvicorn app.main:app --reload
```

The application will be running on [http://localhost:8000](http://localhost:8000).

---

## Endpoint URLs

- **API Health Check (Server Liveness)**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Document Verification Status**: [http://localhost:8000/api/v1/document/status](http://localhost:8000/api/v1/document/status)
- **Face Verification Status**: [http://localhost:8000/api/v1/face/status](http://localhost:8000/api/v1/face/status)
- **Document Upload & OCR**: `POST http://localhost:8000/api/v1/document/upload` (accepts `document_type` and `document_file`)

