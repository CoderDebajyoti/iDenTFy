from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.document import router as document_router
from app.api.face import router as face_router

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System API",
    description="Backend MVP skeleton for document verification, MRZ parsing, tampering forensics, and face matching.",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under api version prefix
app.include_router(document_router, prefix="/api/v1/document", tags=["Document Verification"])
app.include_router(face_router, prefix="/api/v1/face", tags=["Face Verification"])

@app.get("/api/v1/health", tags=["System Health"])
def health_check():
    """
    Health check endpoint to confirm that the backend server is running and healthy.
    """
    return {
        "status": "healthy",
        "service": "identity-document-screening-backend",
        "version": "0.1.0"
    }

@app.get("/", include_in_schema=False)
def root_redirect():
    """
    Redirects root requests to health check endpoint.
    """
    return {
        "message": "Welcome to the AI-Based Fake Identity & Document Screening System API. Refer to /docs for Swagger UI.",
        "health": "/api/v1/health",
        "docs": "/docs"
    }
