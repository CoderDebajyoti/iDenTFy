import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "iDenTFy AI Identity & Document Screening System"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = True

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'identfy.db').replace(chr(92), '/')}"
    )
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    DOCUMENTS_DIR: str = os.path.join(UPLOAD_DIR, "documents")
    FACES_DIR: str = os.path.join(UPLOAD_DIR, "faces")

    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Biometric Threshold
    FACE_SIMILARITY_THRESHOLD: float = 0.68

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure upload directories exist
os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
os.makedirs(settings.FACES_DIR, exist_ok=True)
