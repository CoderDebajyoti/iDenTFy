import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Verify DATABASE_URL is present
if not getattr(settings, "DATABASE_URL", None) or not settings.DATABASE_URL.strip():
    raise RuntimeError(
        "Configuration Error: DATABASE_URL is missing or empty. "
        "A valid PostgreSQL connection string is required."
    )

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (retained strictly for isolated test suites)
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
else:
    # PostgreSQL connection resilience
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a transactional database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

