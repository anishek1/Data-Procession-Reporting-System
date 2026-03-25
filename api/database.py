"""
SQLAlchemy database setup.

Provides the engine, session factory, declarative base,
and the FastAPI get_db dependency.
"""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_config

_config = get_config()
DATABASE_URL: str = _config.get("database_url", "sqlite:///./dprs.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite://") else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
