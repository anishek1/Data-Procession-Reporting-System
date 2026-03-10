"""Tests for data_processor module."""

import pytest
import json
from core.data_processor import (
    load_csv, load_json, load_file,
    compute_statistics, clear_data, get_loaded_data
)
from core.exceptions import FileNotFoundError as DPRSFileNotFoundError
from core.exceptions import InvalidFileTypeError


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_data():
    """Clear loaded data before each test."""
    clear_data()
    yield
    clear_data()


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file with numeric columns."""
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "name,age,salary\n"
        "Alice,30,50000\n"
        "Bob,25,45000\n"
        "Charlie,35,60000\n"
    )
    return str(csv_file)


@pytest.fixture
def sample_json(tmp_path):
    """Create a sample JSON file (array of objects)."""
    json_file = tmp_path / "sample.json"
    data = [
        {"name": "Alice", "age": 30, "salary": 50000},
        {"name": "Bob", "age": 25, "salary": 45000},
        {"name": "Charlie", "age": 35, "salary": 60000},
    ]
    json_file.write_text(json.dumps(data))
    return str(json_file)


# ── load_file / load_csv / load_json ─────────────────────────────────────────

def test_load_csv(sample_csv):
    """load_file should correctly load a CSV and return metadata."""
    result = load_file(sample_csv)
    assert result['status'] == 'success'
    assert result['rows'] == 3
    assert result['columns'] == 3
    assert 'name' in result['headers']
    assert 'age' in result['headers']


def test_load_json(sample_json):
    """load_file should correctly load a JSON array."""
    result = load_file(sample_json)
    assert result['status'] == 'success'
    assert result['rows'] == 3
    assert result['columns'] == 3


def test_load_file_stores_in_memory(sample_csv):
    """Loaded data should be accessible via get_loaded_data."""
    load_file(sample_csv)
    data = get_loaded_data()
    assert data is not None
    assert data['row_count'] == 3


def test_load_nonexistent_file():
    """Loading a file that doesn't exist raises DPRSFileNotFoundError."""
    with pytest.raises(DPRSFileNotFoundError):
        load_file("nonexistent_file.csv")


def test_load_invalid_extension(tmp_path):
    """Loading an unsupported extension raises InvalidFileTypeError."""
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("some data")
    with pytest.raises(InvalidFileTypeError):
        load_file(str(txt_file))


def test_load_csv_with_wrong_extension(tmp_path):
    """Passing a non-CSV to load_csv raises InvalidFileTypeError."""
    json_file = tmp_path / "data.json"
    json_file.write_text("{}")
    with pytest.raises(InvalidFileTypeError):
        load_csv(str(json_file))


def test_load_json_with_wrong_extension(tmp_path):
    """Passing a non-JSON to load_json raises InvalidFileTypeError."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2")
    with pytest.raises(InvalidFileTypeError):
        load_json(str(csv_file))


# ── compute_statistics ────────────────────────────────────────────────────────

def test_compute_statistics_all_columns(sample_csv):
    """compute_statistics should return stats for all numeric columns."""
    load_file(sample_csv)
    stats = compute_statistics()
    assert 'age' in stats
    assert 'salary' in stats
    assert stats['age']['count'] == 3
    assert stats['age']['mean'] == 30.0
    assert stats['age']['min'] == 25.0
    assert stats['age']['max'] == 35.0
    assert stats['salary']['mean'] == 51666.67


def test_compute_statistics_single_column(sample_csv):
    """compute_statistics with a column name only returns that column."""
    load_file(sample_csv)
    stats = compute_statistics(column_name='age')
    assert 'age' in stats
    assert 'salary' not in stats


def test_compute_statistics_no_data():
    """compute_statistics without loaded data raises ValueError."""
    with pytest.raises(ValueError, match="No data loaded"):
        compute_statistics()


# ── clear_data ────────────────────────────────────────────────────────────────

def test_clear_data(sample_csv):
    """clear_data should remove data from memory."""
    load_file(sample_csv)
    assert get_loaded_data() is not None
    clear_data()
    assert get_loaded_data() is None
    with pytest.raises(ValueError):
        compute_statistics()
