"""Tests for validator module."""

import pytest
from core.validator import Schema, validate_schema, clean_data, check_missing_values
from core.exceptions import SchemaValidationError


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_schema():
    """Standard schema used across multiple tests."""
    return Schema({
        'name': {'type': 'string', 'required': True},
        'age': {'type': 'integer', 'required': True},
        'salary': {'type': 'float', 'required': False},
    })


@pytest.fixture
def valid_rows():
    """Three fully valid rows matching sample_schema."""
    return [
        {'name': 'Alice', 'age': '30', 'salary': '50000'},
        {'name': 'Bob', 'age': '25', 'salary': '45000'},
        {'name': 'Charlie', 'age': '35', 'salary': '60000'},
    ]


# ── Schema.validate ───────────────────────────────────────────────────────────

def test_valid_row(sample_schema):
    """A fully valid row should pass validation."""
    row = {'name': 'Alice', 'age': '30', 'salary': '50000'}
    is_valid, error = sample_schema.validate(row)
    assert is_valid is True
    assert error is None


def test_missing_required_field(sample_schema):
    """A row missing a required field should fail."""
    row = {'age': '30', 'salary': '50000'}  # 'name' is missing
    is_valid, error = sample_schema.validate(row)
    assert is_valid is False
    assert 'Required field missing' in error


def test_empty_required_field(sample_schema):
    """An empty string in a required field should fail."""
    row = {'name': '', 'age': '30', 'salary': '50000'}
    is_valid, error = sample_schema.validate(row)
    assert is_valid is False


def test_invalid_integer_type(sample_schema):
    """A non-numeric value for an integer field should fail."""
    row = {'name': 'Alice', 'age': 'not_a_number', 'salary': '50000'}
    is_valid, error = sample_schema.validate(row)
    assert is_valid is False
    assert 'age' in error


def test_optional_field_can_be_missing(sample_schema):
    """An optional field can be absent without failing validation."""
    row = {'name': 'Alice', 'age': '30'}  # salary is optional
    is_valid, error = sample_schema.validate(row)
    assert is_valid is True


def test_float_field_accepts_integer_string(sample_schema):
    """An integer string should be accepted for a float field."""
    row = {'name': 'Alice', 'age': '30', 'salary': '50000'}
    is_valid, error = sample_schema.validate(row)
    assert is_valid is True


# ── validate_schema ───────────────────────────────────────────────────────────

def test_validate_schema_all_valid(sample_schema, valid_rows):
    """validate_schema on all-valid data returns a success dict."""
    data = {'rows': valid_rows, 'headers': ['name', 'age', 'salary']}
    result = validate_schema(data, sample_schema)
    assert result['validation_passed'] is True
    assert result['valid_rows'] == 3
    assert result['invalid_rows'] == 0


def test_validate_schema_raises_on_invalid(sample_schema):
    """validate_schema raises SchemaValidationError if any row is invalid."""
    bad_rows = [
        {'name': 'Alice', 'age': '30'},
        {'name': '', 'age': '25'},   # empty required field
    ]
    data = {'rows': bad_rows, 'headers': ['name', 'age']}
    with pytest.raises(SchemaValidationError):
        validate_schema(data, sample_schema)


# ── clean_data ────────────────────────────────────────────────────────────────

def test_clean_data_removes_invalid_rows(sample_schema):
    """clean_data should keep only rows that pass validation."""
    rows = [
        {'name': 'Alice', 'age': '30', 'salary': '50000'},
        {'name': 'Bob', 'age': 'bad', 'salary': '45000'},  # invalid age
        {'name': 'Charlie', 'age': '35', 'salary': '60000'},
    ]
    cleaned = clean_data(rows, sample_schema)
    assert len(cleaned) == 2
    assert cleaned[0]['name'] == 'Alice'
    assert cleaned[1]['name'] == 'Charlie'


def test_clean_data_all_valid(sample_schema, valid_rows):
    """clean_data should return all rows if none are invalid."""
    cleaned = clean_data(valid_rows, sample_schema)
    assert len(cleaned) == len(valid_rows)


# ── check_missing_values ──────────────────────────────────────────────────────

def test_check_missing_values_detects_gaps():
    """check_missing_values should detect None and empty-string as missing."""
    rows = [
        {'name': 'Alice', 'age': '30', 'email': 'alice@example.com'},
        {'name': 'Bob', 'age': '', 'email': None},
        {'name': 'Charlie', 'age': '35', 'email': 'charlie@example.com'},
    ]
    missing = check_missing_values(rows)
    assert 'age' in missing
    assert missing['age']['missing_count'] == 1
    assert missing['age']['missing_percentage'] == pytest.approx(
        33.33, abs=0.01
    )
    assert 'email' in missing
    assert missing['email']['missing_count'] == 1


def test_check_missing_values_no_gaps():
    """check_missing_values returns empty dict when all values are present."""
    rows = [
        {'name': 'Alice', 'age': '30'},
        {'name': 'Bob', 'age': '25'},
    ]
    missing = check_missing_values(rows)
    assert missing == {}


def test_check_missing_values_empty_input():
    """check_missing_values returns empty dict for empty dataset."""
    assert check_missing_values([]) == {}
