"""Tests for the FastAPI endpoints."""

import io
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from api.database import Base, get_db
from api.main import app
from core.data_processor import clear_data

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def override_db():
    """Use a fresh in-memory SQLite database for every test.

    StaticPool ensures all connections share the same in-memory database
    so tables created by create_all are visible to every session.
    """
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def _get_test_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db

    # Clear DataProcessor singleton state and disk cache before each test
    clear_data()

    yield

    # Tear down: clear DataProcessor state and disk cache again
    clear_data()
    Base.metadata.drop_all(engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def csv_bytes():
    """Minimal valid CSV content."""
    return b"name,age,salary\nAlice,30,50000\nBob,25,45000\nCharlie,35,60000\n"


@pytest.fixture
def json_bytes():
    """Minimal valid JSON content (array of objects)."""
    data = [
        {"name": "Alice", "age": 30, "salary": 50000},
        {"name": "Bob", "age": 25, "salary": 45000},
    ]
    return json.dumps(data).encode()


# ── POST /upload ──────────────────────────────────────────────────────────────

def test_upload_valid_csv(client, csv_bytes):
    """Uploading a valid CSV returns 200 with job_id and statistics."""
    response = client.post(
        "/upload",
        files={"file": ("test_data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert "job_id" in body
    assert body["filename"] == "test_data.csv"
    assert body["rows"] == 3
    assert body["columns"] == 3
    assert "age" in body["statistics"]
    assert "salary" in body["statistics"]


def test_upload_valid_json(client, json_bytes):
    """Uploading a valid JSON array returns 200 with correct metadata."""
    response = client.post(
        "/upload",
        files={"file": ("test_data.json", io.BytesIO(json_bytes), "application/json")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["rows"] == 2
    assert "job_id" in body


def test_upload_invalid_extension(client):
    """Uploading an unsupported file type returns HTTP 400."""
    response = client.post(
        "/upload",
        files={"file": ("data.txt", io.BytesIO(b"some text"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_empty_csv(client):
    """Uploading a CSV with headers but no rows returns 200 with 0 rows."""
    response = client.post(
        "/upload",
        files={"file": ("empty.csv", io.BytesIO(b"name,age\n"), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 0
    assert body["status"] == "completed"


def test_upload_creates_job_record(client, csv_bytes):
    """A successful upload creates a retrievable job record in the database."""
    upload_resp = client.post(
        "/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert upload_resp.status_code == 200
    job_id = upload_resp.json()["job_id"]

    # Verify via the status endpoint (no direct store access needed)
    status_resp = client.get(f"/jobs/{job_id}")
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["status"] == "completed"
    assert body["rows"] == 3


# ── GET /jobs/{job_id} ────────────────────────────────────────────────────────

def test_get_job_valid_id(client, csv_bytes):
    """After upload, GET /jobs/{job_id} returns the full job record."""
    upload_resp = client.post(
        "/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    job_id = upload_resp.json()["job_id"]

    status_resp = client.get(f"/jobs/{job_id}")
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["job_id"] == job_id
    assert body["status"] == "completed"
    assert body["rows"] == 3
    assert "age" in body["statistics"]
    assert "created_at" in body


def test_get_job_invalid_id(client):
    """GET /jobs/{job_id} with unknown id returns HTTP 404."""
    response = client.get("/jobs/nonexistent-id-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_job_contains_all_fields(client, csv_bytes):
    """Job status response includes all expected fields."""
    upload_resp = client.post(
        "/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    job_id = upload_resp.json()["job_id"]
    body = client.get(f"/jobs/{job_id}").json()

    for field in ("job_id", "status", "filename", "rows", "columns", "headers", "statistics", "created_at"):
        assert field in body, f"Missing field: {field}"


# ── GET /health ───────────────────────────────────────────────────────────────

def test_health_check(client):
    """Health endpoint returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Security / error-path regression tests ───────────────────────────────────

def test_upload_traversal_filename(client):
    """Uploading a file with a path traversal filename is rejected with HTTP 400."""
    response = client.post(
        "/upload",
        files={"file": ("../secret.csv", io.BytesIO(b"a,b\n1,2\n"), "text/csv")},
    )
    assert response.status_code == 400
    assert "job_id" not in response.json()


def test_upload_malformed_json(client):
    """Uploading a JSON file with invalid syntax returns HTTP 422."""
    response = client.post(
        "/upload",
        files={"file": ("data.json", io.BytesIO(b"[not valid json"), "application/json")},
    )
    assert response.status_code == 422
    assert "job_id" not in response.json()


def test_upload_malformed_csv(client):
    """Uploading a CSV with inconsistent column counts returns 200 (DictReader is tolerant)."""
    response = client.post(
        "/upload",
        files={
            "file": (
                "data.csv",
                io.BytesIO(b"a,b,c\n1,2\n3,4,5,6\n"),
                "text/csv",
            )
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 2
    assert body["status"] == "completed"
