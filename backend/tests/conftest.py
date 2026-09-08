import os
import sys

# Ensure backend directory is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

TEST_DB_PATH = os.path.join(backend_dir, "tests", "test_isolated.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

import pytest
import sqlite3
from database.database import Base, engine, SessionLocal
from database.models import Person, Document, Passport, Visa

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Isolated test database runner fixture.
    Ensures all pytest tests execute in an isolated database and never pollute the
    production/development identfy.db database.
    """
    # Create schema in test database
    Base.metadata.create_all(bind=engine)

    # Seed reference registry documents into isolated test database
    live_db_path = os.path.join(backend_dir, "database", "identfy.db")
    if os.path.exists(live_db_path):
        live_conn = sqlite3.connect(live_db_path)
        test_conn = sqlite3.connect(TEST_DB_PATH)
        try:
            for table in ["persons", "documents", "passports", "visas"]:
                cursor = live_conn.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                if rows and cursor.description:
                    cols = [d[0] for d in cursor.description]
                    placeholders = ", ".join(["?"] * len(cols))
                    col_names = ", ".join(cols)
                    test_conn.executemany(
                        f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})",
                        rows
                    )
            test_conn.commit()
        except Exception as e:
            print(f"Notice during test db seed: {e}")
        finally:
            live_conn.close()
            test_conn.close()

    yield

    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
