# iDenTFy
Al-Based Fake Identity &amp; Document Screening System
Rudra

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

