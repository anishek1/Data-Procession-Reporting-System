"""
FastAPI application entry point for DPRS.

Run with:
    uvicorn api.main:app --reload

Interactive docs available at:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from api.database import Base, engine
from api import db_models  # noqa: F401 — registers Job model with Base
from api.routes import jobs, upload

app = FastAPI(
    title="Data Processing & Reporting System API",
    description="REST API for uploading data files and retrieving processing results.",
    version="1.0.0",
)


@app.on_event("startup")
def create_tables() -> None:
    """Create all database tables on startup if they do not already exist."""
    Base.metadata.create_all(bind=engine)


app.include_router(upload.router, tags=["upload"])
app.include_router(jobs.router, tags=["jobs"])


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok"}
