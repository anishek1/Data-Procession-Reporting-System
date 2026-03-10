"""
Data Validation Module

Validates data schema and integrity.
Handles missing values, type checking, and data quality.
"""

from typing import Dict, List, Any, Optional, Tuple
from .exceptions import SchemaValidationError
import logging

logger = logging.getLogger(__name__)


class Schema:
    """Define a data schema with field requirements and type constraints."""

    def __init__(self, fields: Dict[str, Dict[str, Any]]):
        """
        Initialize schema.

        Args:
            fields: Dict of field_name -> {
                'type': 'string' | 'integer' | 'float' | 'boolean',
                'required': True | False
            }
        """
        self.fields = fields

    def validate(self, row: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a single row against the schema.

        Args:
            row: Dict representing one data row

        Returns:
            Tuple of (is_valid, error_message). error_message is None if valid.
        """
        for field_name, field_config in self.fields.items():
            # Check if the schema enforces this field as mandatory
            if field_config.get('required', False):
                # Field is missing if key isn't in row, is None, or is empty
                if field_name not in row or row[field_name] is None or row[field_name] == '':
                    return False, f"Required field missing: {field_name}"

            # Only validate the type if a value is actually present
            if field_name in row and row[field_name] is not None and row[field_name] != '':
                value = row[field_name]
                expected_type = field_config.get('type', 'string')

                # If the value doesn't match the expected type, fail the validation
                if not self._check_type(value, expected_type):
                    return False, (
                        f"Field '{field_name}': expected {expected_type}, "
                        f"got '{value}'"
                    )

        return True, None

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if a value matches the expected type string."""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'integer':
            try:
                int(value)
                return True
            except (ValueError, TypeError):
                return False
        elif expected_type == 'float':
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        elif expected_type == 'boolean':
            if isinstance(value, bool):
                return True
            if isinstance(value, str):
                return value.lower() in ('true', 'false', 'yes', 'no', '0', '1')
            return False
        return True  # Unknown type — pass through


def validate_schema(data: Dict[str, Any], schema: Schema) -> Dict[str, Any]:
    """
    Validate entire dataset against a Schema.

    Args:
        data: Dict with 'rows' and 'headers' keys
        schema: Schema instance to validate against

    Returns:
        Dict with validation summary

    Raises:
        SchemaValidationError: If any row fails validation
    """
    rows = data.get('rows', [])
    valid_rows = []
    invalid_rows = []

    for idx, row in enumerate(rows):
        # Validate each row individually using the provided schema object
        is_valid, error_msg = schema.validate(row)

        if is_valid:
            valid_rows.append(row)
        else:
            # Keep track of invalid rows and their specific errors for reporting
            invalid_rows.append({'row_index': idx, 'error': error_msg, 'data': row})

    if invalid_rows:
        logger.warning(f"Schema validation: {len(invalid_rows)} invalid rows found")
        raise SchemaValidationError(
            f"Schema validation failed for {len(invalid_rows)} rows. "
            f"First error: {invalid_rows[0]['error']}"
        )

    logger.info(f"Schema validation passed: {len(valid_rows)} rows valid")
    return {
        'valid_rows': len(valid_rows),
        'invalid_rows': len(invalid_rows),
        'total_rows': len(rows),
        'validation_passed': True
    }


def clean_data(rows: List[Dict[str, Any]], schema: Schema) -> List[Dict[str, Any]]:
    """
    Clean data by removing rows that fail schema validation.

    Args:
        rows: List of row dicts
        schema: Schema to validate against

    Returns:
        List of rows that passed validation
    """
    # Filter out rows that do not pass schema validation, keeping only valid ones
    cleaned = [row for row in rows if schema.validate(row)[0]]

    # Calculate how many rows were dropped for logging purposes
    removed = len(rows) - len(cleaned)
    logger.info(
        f"Data cleaning: {len(rows)} rows → {len(cleaned)} rows "
        f"(removed {removed} invalid)"
    )
    return cleaned


def check_missing_values(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check for missing or empty values in a dataset.

    Args:
        rows: List of row dicts

    Returns:
        Dict of column_name -> {missing_count, missing_percentage}
        Only columns with missing values are included.
    """
    if not rows:
        return {}

    headers = list(rows[0].keys())
    missing_stats = {}

    for header in headers:
        missing_count = sum(
            1 for row in rows
            if row.get(header) is None or row.get(header) == ''
        )
        if missing_count > 0:
            missing_stats[header] = {
                'missing_count': missing_count,
                'missing_percentage': round((missing_count / len(rows)) * 100, 2)
            }

    return missing_stats
