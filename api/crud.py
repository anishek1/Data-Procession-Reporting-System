"""
CRUD operations for the Job model.

All functions accept a SQLAlchemy Session and operate on the jobs table.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from api.db_models import Job


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


def create_job(db: Session, job_id: str, filename: str) -> Job:
    """Insert a new job row with status 'processing' and return it."""
    job = Job(
        job_id=job_id,
        status="processing",
        filename=filename,
        created_at=_utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job(db: Session, job_id: str, **fields: Any) -> bool:
    """Apply field updates to an existing job row and commit.

    Returns True if the job was found and updated, False if not found.
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job is None:
        return False
    forbidden_fields = {"job_id", "created_at"}
    valid_columns = {col.name for col in Job.__table__.columns}
    allowed_columns = valid_columns - forbidden_fields

    invalid_keys = [key for key in fields if key not in allowed_columns]
    if invalid_keys:
        raise ValueError(f"Invalid field(s) for Job update: {invalid_keys}")

    for key, value in fields.items():
        setattr(job, key, value)
    job.updated_at = _utcnow()
    db.commit()
    return True


def get_job(db: Session, job_id: str) -> Optional[Job]:
    """Return the Job ORM object for job_id, or None if not found."""
    return db.query(Job).filter(Job.job_id == job_id).first()
