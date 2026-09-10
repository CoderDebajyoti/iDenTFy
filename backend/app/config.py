import os
from typing import List, Any
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE = os.path.join(_BASE_DIR, ".env")

# Reliably load backend/.env regardless of current working directory
# override=False preserves explicitly set environment variables (e.g., test runner isolation)
if os.path.exists(_ENV_FILE):
    load_dotenv(_ENV_FILE, override=False)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="allow"
    )

    PROJECT_NAME: str = "iDenTFy AI Identity & Document Screening System"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = True

    BASE_DIR: str = _BASE_DIR
    DATABASE_URL: str = ""
    UPLOAD_DIR: str = os.path.join(_BASE_DIR, "uploads")
    DOCUMENTS_DIR: str = os.path.join(UPLOAD_DIR, "documents")
    TEMP_DIR: str = os.path.join(UPLOAD_DIR, "temp")
    FACES_DIR: str = os.path.join(UPLOAD_DIR, "faces")

    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Biometric Threshold
    FACE_SIMILARITY_THRESHOLD: float = 0.68

    # Database Matching Flags (Production screening keeps database matching disabled / bypassed by default)
    DATABASE_MATCHING_ENABLED: bool = False
    BYPASS_DATABASE_MATCHING: bool = True

    # Frontend URL & CORS
    FRONTEND_URL: str = ""
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        origins = list(v) if isinstance(v, (list, tuple)) else ([i.strip() for i in str(v).split(",") if i.strip()] if v else [])
        frontend_url = os.environ.get("FRONTEND_URL", "").strip()
        if frontend_url:
            for u in frontend_url.split(","):
                u_clean = u.strip().rstrip("/")
                if u_clean and u_clean not in origins:
                    origins.append(u_clean)
        return origins if origins else ["*"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        val = (v or os.environ.get("DATABASE_URL") or "").strip()
        if not val:
            raise ValueError(
                "Configuration Error: DATABASE_URL is missing or empty. "
                "Ensure a valid PostgreSQL connection string is provided."
            )
        # Render PostgreSQL compatibility: SQLAlchemy 2.0 requires postgresql://
        if val.startswith("postgres://"):
            val = val.replace("postgres://", "postgresql://", 1)
        return val

try:
    settings = Settings()
except Exception as e:
    raise RuntimeError(
        f"Configuration Error: Failed to initialize application settings. "
        f"Ensure backend/.env contains a valid DATABASE_URL. Details: {e}"
    ) from e

# Ensure upload directories exist
os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.FACES_DIR, exist_ok=True)

