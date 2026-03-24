"""
POST /upload endpoint.

Accepts a CSV or JSON file, saves it to the input directory,
runs load_file + compute_statistics, and records the result as a job.
"""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api import crud
from api.database import get_db
from api.models import UploadResponse
from core.data_processor import clear_data, compute_statistics, load_file
from core.exceptions import DPRSException
from utils.config import get_config
from utils.logger import logger

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".json"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
) -> UploadResponse:
    """
    Upload a CSV or JSON data file for processing.

    - Validates file extension (.csv or .json only)
    - Saves the file to the configured input directory
    - Runs statistical analysis immediately
    - Returns a job_id plus the computed statistics
    """
    # Validate file extension before doing any disk I/O
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Only .csv and .json are accepted.",
        )

    job_id = str(uuid.uuid4())
    crud.create_job(db, job_id, file.filename)
    logger.info(f"Job {job_id}: upload started for '{file.filename}'")

    # Determine destination path from config
    config = get_config()
    input_dir = config.get("input_dir", "input")
    os.makedirs(input_dir, exist_ok=True)
    dest_path = os.path.join(input_dir, file.filename)

    # Save uploaded file to disk
    try:
        with open(dest_path, "wb") as dest:
            shutil.copyfileobj(file.file, dest)
    except Exception as exc:
        crud.update_job(db, job_id, status="failed", error=str(exc))
        logger.error(f"Job {job_id}: failed to save file — {exc}")
        raise HTTPException(status_code=422, detail=f"Could not save file: {exc}")

    # Process the file using existing core module
    try:
        clear_data()
        file_meta = load_file(dest_path)
        statistics = compute_statistics()
    except (DPRSException, ValueError) as exc:
        crud.update_job(db, job_id, status="failed", error=str(exc))
        logger.error(f"Job {job_id}: processing failed — {exc}")
        raise HTTPException(status_code=422, detail=str(exc))

    # Persist result in database
    crud.update_job(
        db,
        job_id,
        status="completed",
        rows=file_meta["rows"],
        columns=file_meta["columns"],
        headers=file_meta["headers"],
        statistics=statistics,
    )
    logger.info(f"Job {job_id}: completed — {file_meta['rows']} rows, {file_meta['columns']} columns")

    return UploadResponse(
        job_id=job_id,
        status="completed",
        filename=file.filename,
        rows=file_meta["rows"],
        columns=file_meta["columns"],
        headers=file_meta["headers"],
        statistics=statistics,
    )
