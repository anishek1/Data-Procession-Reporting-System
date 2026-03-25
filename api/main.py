"""
FastAPI application entry point for DPRS.

Run with:
    uvicorn api.main:app --reload

Interactive docs available at:
    http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import Base, engine
from api import db_models  # noqa: F401 — registers Job model with Base
from api.routes import jobs, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Data Processing & Reporting System API",
    description="REST API for uploading data files and retrieving processing results.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(upload.router, tags=["upload"])
app.include_router(jobs.router, tags=["jobs"])


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok"}
