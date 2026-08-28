import os
import sys
from dotenv import load_dotenv

# Ensure we're in the right directory and add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from database.connection import engine
from database.base import Base
import database.models  # Ensure models are loaded
from database.seed.seed_data import seed_database
import alembic.config
import alembic.command

def init_database():
    print("Initializing Database...")
    
    # Run Alembic migrations
    print("Applying migrations...")
    alembic_cfg = alembic.config.Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    alembic.command.upgrade(alembic_cfg, "head")
    
    # Seed data
    seed_database()
    
    print("Database initialization complete.")

if __name__ == "__main__":
    init_database()
