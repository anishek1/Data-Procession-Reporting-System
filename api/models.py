"""
Pydantic models for FastAPI request and response validation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Response returned immediately after a successful file upload and processing."""

    job_id: str
    status: str
    filename: str
    rows: int
    columns: int
    headers: List[str]
    statistics: Dict[str, Any]


class JobStatusResponse(BaseModel):
    """Full job record returned by the job status endpoint."""

    job_id: str
    status: str
    filename: str
    rows: Optional[int] = None
    columns: Optional[int] = None
    headers: Optional[List[str]] = None
    statistics: Optional[Dict[str, Any]] = None
    created_at: str
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str
