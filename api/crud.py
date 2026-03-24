"""
CRUD operations for the Job model.

All functions accept a SQLAlchemy Session and operate on the jobs table.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from api.db_models import Job


def _utcnow() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


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


def update_job(db: Session, job_id: str, **fields: Any) -> None:
    """Apply field updates to an existing job row and commit."""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job is None:
        return
    for key, value in fields.items():
        setattr(job, key, value)
    job.updated_at = _utcnow()
    db.commit()


def get_job(db: Session, job_id: str) -> Optional[Job]:
    """Return the Job ORM object for job_id, or None if not found."""
    return db.query(Job).filter(Job.job_id == job_id).first()
