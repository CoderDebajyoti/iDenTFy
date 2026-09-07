"""
iDenTFy — AI Identity & Document Screening System API
Main FastAPI Application Entrypoint
"""

import sys
import os

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api.document import router as document_router
from app.api.face import router as face_router
from app.api.verification import router as verification_router
from database.database import engine, Base
from database.seed import seed_database

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "AI-Powered Fake Identity & Document Screening System. "
        "Provides automated OCR, MRZ checksum validation, registry database matching, "
        "digital tampering forensics, 1:1 biometric face verification, and composite risk scoring."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers (Prevent exposing raw internal tracebacks to users)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        msg = err.get("msg", "Invalid field input.")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "Validation Error", "details": errors}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing the request. Please try again or consult the system administrator."
        }
    )

# Root ping endpoint
@app.get("/", tags=["General"])
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "operational",
        "version": "1.0.0",
        "api_docs": "/docs",
        "health": "/api/v1/health"
    }

# Register API v1 Routers
app.include_router(verification_router, prefix=settings.API_V1_STR)
app.include_router(document_router, prefix=settings.API_V1_STR)
app.include_router(face_router, prefix=settings.API_V1_STR)

# Also expose direct health at /health
@app.get("/health", include_in_schema=False)
def direct_health(request: Request):
    from app.api.verification import system_health_check
    from database.database import SessionLocal
    db = SessionLocal()
    try:
        return system_health_check(db)
    finally:
        db.close()
