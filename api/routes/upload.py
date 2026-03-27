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

from api import crud
from api.database import get_db
from api.models import UploadResponse
from core.data_processor import process_file
from core.exceptions import InvalidFileTypeError
from utils.config import get_config
from utils.file_utils import validate_file_type, secure_resolve_path
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
    # Validate file extension before doing any disk I/O or DB writes
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename in upload.")
        
    try:
        validate_file_type(filename, ALLOWED_EXTENSIONS)
    except InvalidFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    job_id = str(uuid.uuid4())
    crud.create_job(db, job_id, filename)
    logger.info(f"Job {job_id}: upload started for '{filename}'")

    # Determine destination path from config — prefix with job_id to avoid collisions
    config = get_config()
    input_dir = config.get("input_dir", "input")
    os.makedirs(input_dir, exist_ok=True)
    
    try:
        # Resolving path safely using the secure file path resolver
        dest_path = str(secure_resolve_path(input_dir, f"{job_id}_{filename}"))
    except ValueError as exc:
        crud.update_job(db, job_id, status="failed", error=str(exc))
        logger.warning(f"Rejected upload with invalid filename: '{filename}', error: {exc}")
        raise HTTPException(status_code=400, detail="Invalid filename.")

    # Save uploaded file to disk
    try:
        with open(dest_path, "wb") as dest:
            shutil.copyfileobj(file.file, dest)
    except OSError as exc:
        crud.update_job(db, job_id, status="failed", error=str(exc))
        logger.error(f"Job {job_id}: failed to save file — {exc}")
        raise HTTPException(status_code=422, detail=f"Could not save file: {exc}") from exc

    # Process the file atomically (no shared singleton state touched)
    try:
        file_meta, statistics = process_file(dest_path)
    except Exception as exc:
        crud.update_job(db, job_id, status="failed", error=str(exc))
        logger.error(f"Job {job_id}: processing failed — {exc}")
        raise HTTPException(status_code=422, detail=str(exc)) from exc

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
        filename=filename,
        rows=file_meta["rows"],
        columns=file_meta["columns"],
        headers=file_meta["headers"],
        statistics=statistics,
    )
