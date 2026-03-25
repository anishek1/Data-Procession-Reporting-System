"""
GET /jobs/{job_id} endpoint.

Retrieves job status and results from the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import crud
from api.database import get_db
from api.models import JobStatusResponse
from utils.logger import logger

router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
) -> JobStatusResponse:
    """
    Retrieve the status and results for a previously submitted job.

    - Returns the full job record including statistics on completion
    - Returns HTTP 404 if the job_id does not exist
    """
    job = crud.get_job(db, job_id)
    if job is None:
        logger.warning(f"Job status requested for unknown job_id: '{job_id}'")
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found.",
        )

    logger.info(f"Job status retrieved for job_id: '{job_id}' — status: {job.status}")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        filename=job.filename,
        rows=job.rows,
        columns=job.columns,
        headers=job.headers,
        statistics=job.statistics,
        created_at=job.created_at.isoformat(),
        error=job.error,
    )
