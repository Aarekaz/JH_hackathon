from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get the current directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "ai_parliament.db")

# Create database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with proper permissions
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Needed for SQLite
        "timeout": 30  # Add timeout for busy database
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
