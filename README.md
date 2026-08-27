# iDenTFy
Al-Based Fake Identity &amp; Document Screening System

```

                        REACT UI
                           │
                           │
                    VERIFY DOCUMENT
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │   Backend   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
            OCR          MRZ        Image/Metadata
              │            │            │
              ▼            ▼            ▼
         Field Data    Checksum    Forensic Signals
              │            │            │
              └────────────┼────────────┘
                           ▼
                    VALIDATION ENGINE
                           │
                           ▼
                    TAMPERING ENGINE
                           │
                           ▼
                    FACE VERIFICATION
                           │
                           ▼
                     RISK ENGINE
                           │
                           ▼
                       RESPONSE
                           │
                           ▼
                  YOUR EXISTING UI
```

process::

```
                DOCUMENT UPLOAD
                       │
                       ▼
              ┌─────────────────┐
              │  ID VERIFICATION │
              └────────┬────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
        FAILED                   APPROVED
          │                         │
          ▼                         ▼
    STOP PROCESSING          FACE VERIFICATION
                                      │
                                      ▼
                              ┌───────────────┐
                              │ Face Matching │
                              └───────┬───────┘
                                      │
                           ┌──────────┴──────────┐
                           │                     │
                         MATCH                MISMATCH
                           │                     │
                           ▼                     ▼
                        APPROVED              HIGH RISK
```

## Project Progress

### Backend Progress

The backend is currently at **Phase 2: Document Upload and OCR**. It is built with FastAPI and exposes versioned API routes under `/api/v1`.

Completed so far:

- FastAPI application foundation with root, health, document, and face routes.
- Document type validation for passports, identity cards, residence permits, and driver licenses.
- Upload validation for file size, extension, MIME type, and decoded image content.
- Temporary file handling with generated filenames and cleanup after processing.
- Image quality analysis for resolution, blur, and brightness.
- Image preprocessing using bilateral denoising and CLAHE contrast enhancement.
- PaddleOCR integration with extracted text, confidence values, and bounding-box coordinates.
- Automated backend coverage for health checks, valid uploads, quality conditions, invalid images, unsupported formats, oversized files, and invalid document types.

The document upload endpoint currently accepts `document_type` and `document_file` and returns the processing status, selected document type, image-quality information, and OCR output. The face-verification and document-status endpoints are currently status placeholders. MRZ parsing, checksum validation, field validation, tampering forensics, face matching, risk scoring, and database integration remain planned work.

### Frontend Progress

The frontend is a React application powered by Vite. The current user flow includes:

- A login screen with email and password fields, password visibility toggle, validation feedback, remember-me control, and a placeholder password-reset action.
- Frontend-only authentication that opens the verification workflow after a successful form submission.
- A three-step verification interface: document type selection, file verification, and results.
- Support for identity cards, passports, residence permits, and driver licenses in the document-type selector.
- Document upload and optional face-image upload controls with selected-file details and removal actions.
- A results view showing mock OCR, tampering, face-verification, risk-score, and overall-status data.
- Responsive styling for desktop and mobile layouts.

The frontend verification result is currently simulated with local state and a delay. The API helper is prepared for integration, but it does not yet match the backend upload contract, so connecting the real verification request is the next integration step.

## Current Development Roadmap

1. Connect the frontend upload flow to `POST /api/v1/document/upload`.
2. Add MRZ extraction, parsing, and checksum validation.
3. Add document field validation and fuzzy matching.
4. Implement tampering detection and metadata analysis.
5. Implement face verification and risk scoring.
6. Add persistence and production authentication with PostgreSQL integration.

## Contributors

### iDenTFy Development Team

The project is developed and maintained by the iDenTFy project team. Individual contributor names are not currently recorded in the repository metadata; this section should be updated with each contributor's name, role, and profile as the team information is finalized.

- **Project team** - Backend, frontend, integration, testing, and documentation




