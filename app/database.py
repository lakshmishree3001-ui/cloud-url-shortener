"""
Database configuration and session management module.
Lab 6: SQLite Database Engine & Session Factory
Lab 13: 12-Factor Cloud & Containerized Database Configuration
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configurable database URL (12-Factor cloud configuration)
# Defaults to urls.db in project root if not specified via environment variable
DEFAULT_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "urls.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE}")

# Automatically ensure parent directory exists for SQLite files (e.g., in Docker /app/data)
if DATABASE_URL.startswith("sqlite:///"):
    sqlite_file = DATABASE_URL.replace("sqlite:///", "")
    if sqlite_file and sqlite_file != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(sqlite_file)), exist_ok=True)

# Create SQLAlchemy engine
# check_same_thread=False allows FastAPI async endpoints across worker threads in SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
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
