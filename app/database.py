"""
Database configuration and session management module.
Lab 6: SQLite Database Engine & Session Factory
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file path: urls.db in project root
DB_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "urls.db"))
DATABASE_URL = f"sqlite:///{DB_FILE_PATH}"

# Create SQLite engine
# check_same_thread=False allows FastAPI async endpoints across multiple threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True for verbose SQL query logging
)

# Create SessionLocal class for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides an isolated database session per request.
    Ensures sessions are cleanly closed when requests complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all database tables defined by models that inherit from Base.
    Idempotent: will not overwrite existing tables or data.
    """
    Base.metadata.create_all(bind=engine)
