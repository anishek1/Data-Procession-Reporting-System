"""
SQLAlchemy ORM models.

Defines the Job table that persists job metadata to SQLite.
"""

from sqlalchemy import Column, DateTime, Integer, JSON, String

from api.database import Base


class Job(Base):
    """Represents a single data processing job."""

    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, default="processing")
    filename = Column(String, nullable=False)
    rows = Column(Integer, nullable=True)
    columns = Column(Integer, nullable=True)
    headers = Column(JSON, nullable=True)
    statistics = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(String, nullable=True)
