from app.api.document import router as document_router
from app.api.face import router as face_router
from app.api.verification import router as verification_router

__all__ = ["document_router", "face_router", "verification_router"]
