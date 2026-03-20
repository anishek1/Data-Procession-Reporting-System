"""
Data Processing Module

Handles file loading, data parsing, and statistical calculations.
Supports CSV and JSON formats.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .exceptions import FileNotFoundError as DPRSFileNotFoundError
from .exceptions import InvalidFileTypeError

# Global variable to store loaded data in memory
_loaded_data: Optional[Dict[str, Any]] = None


def load_csv(filepath: str) -> Dict[str, List[Any]]:
    """
    Load a CSV file and return structured data.

    Args:
        filepath: Path to CSV file

    Returns:
        Dict with 'headers', 'rows', 'row_count', 'column_count' keys

    Raises:
        DPRSFileNotFoundError: If file doesn't exist
        InvalidFileTypeError: If file is not CSV
    """
    filepath = Path(filepath)

    # Ensure the file exists before attempting to read
    if not filepath.exists():
        raise DPRSFileNotFoundError(f"File not found: {filepath}")

    # Validate that we only process CSV files in this function
    if filepath.suffix.lower() != '.csv':
        raise InvalidFileTypeError(
            f"Expected .csv file, got {filepath.suffix}"
        )

    try:
        # Open file with utf-8 encoding to prevent Unicode errors
        with open(filepath, 'r', encoding='utf-8') as f:
            # Use DictReader to automatically map headers to values
            reader = csv.DictReader(f)
            # Extract headers, fallback to empty list if file is empty
            headers = list(reader.fieldnames) if reader.fieldnames else []
            # Read all rows into memory as a list of dictionaries
            rows = list(reader)

        return {
            'headers': headers,
            'rows': rows,
            'row_count': len(rows),
            'column_count': len(headers)
        }
    except Exception as e:
        raise DPRSFileNotFoundError(f"Error reading CSV file: {str(e)}")


def load_json(filepath: str) -> Dict[str, List[Any]]:
    """
    Load a JSON file (array of objects format).

    Args:
        filepath: Path to JSON file

    Returns:
        Dict with 'headers', 'rows', 'row_count', 'column_count' keys

    Raises:
        DPRSFileNotFoundError: If file doesn't exist
        InvalidFileTypeError: If file is not JSON or has wrong format
    """
    filepath = Path(filepath)

    # Check existence to provide a clear error message early
    if not filepath.exists():
        raise DPRSFileNotFoundError(f"File not found: {filepath}")

    # Enforce correct file extension
    if filepath.suffix.lower() != '.json':
        raise InvalidFileTypeError(
            f"Expected .json file, got {filepath.suffix}"
        )

    try:
        # Load the entire JSON structure into memory
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # The application expects a list of records (array of JSON objects)
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")

        # Handle empty JSON arrays gracefully
        if len(data) == 0:
            return {
                'headers': [],
                'rows': [],
                'row_count': 0,
                'column_count': 0
            }

        # Extract headers from the keys of the first object
        headers = list(data[0].keys())

        return {
            'headers': headers,
            'rows': data,
            'row_count': len(data),
            'column_count': len(headers)
        }
    except json.JSONDecodeError as e:
        raise InvalidFileTypeError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise DPRSFileNotFoundError(f"Error reading JSON file: {str(e)}")


def load_file(filepath: str) -> Dict[str, Any]:
    """
    Load a data file (CSV or JSON) based on file extension.
    Stores data in global memory for later processing.

    Args:
        filepath: Path to CSV or JSON file

    Returns:
        Dict with status, file path, row/column counts, and headers

    Raises:
        DPRSFileNotFoundError: If file doesn't exist
        InvalidFileTypeError: If format not supported
    """
    global _loaded_data

    filepath = Path(filepath)

    # Route the file to the appropriate loader based on its extension
    if filepath.suffix.lower() == '.csv':
        data = load_csv(str(filepath))
    elif filepath.suffix.lower() == '.json':
        data = load_json(str(filepath))
    else:
        # Reject unsupported files immediately
        raise InvalidFileTypeError(
            f"Unsupported file format: {filepath.suffix}. Use .csv or .json"
        )

    # Cache the loaded data in memory for subsequent operations
    _loaded_data = data
    
    # Persist the data to a local cache file for stateless CLI workflows
    try:
        with open('.dprs_cache.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception:
        pass  # Fail gracefully if we cannot write to disk

    return {
        'status': 'success',
        'file': str(filepath),
        'rows': data['row_count'],
        'columns': data['column_count'],
        'headers': data['headers']
    }


def get_loaded_data() -> Optional[Dict[str, Any]]:
    """Get the currently loaded data from memory."""
    return _loaded_data


def compute_statistics(column_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute statistical summary of loaded data.

    Args:
        column_name: If specified, compute stats for only this column.
                     If None, compute for all numeric columns.

    Returns:
        Dict mapping column names to their statistics

    Raises:
        ValueError: If no data has been loaded
    """
    global _loaded_data
    if _loaded_data is None:
        # Try to retrieve from disk cache for CLI state persistence
        cache_path = Path('.dprs_cache.json')
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    _loaded_data = json.load(f)
            except Exception:
                pass

    if _loaded_data is None:
        raise ValueError("No data loaded. Call load_file() first.")

    rows = _loaded_data['rows']
    headers = _loaded_data['headers']

    if len(rows) == 0:
        return {'error': 'No data rows to process'}

    stats = {}
    # If the user didn't specify a column, process all headers from the file
    columns_to_process = [column_name] if column_name else headers

    for col in columns_to_process:
        # Skip columns that don't actually exist in the data
        if col not in headers:
            stats[col] = {'error': f"Column '{col}' not found"}
            continue

        numeric_values = []
        # Iterate over every row to extract values for the current column
        for row in rows:
            val = row.get(col)
            # Only process non-null, non-empty values
            if val is not None and val != '':
                try:
                    # Attempt to cast the value to a float for math operations
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    # Ignore non-numeric values (e.g. 'Male', 'Female')
                    pass

        # If we successfully extracted any numeric values, compute their stats
        if numeric_values:
            stats[col] = _compute_column_stats(numeric_values, col)

    return stats


def _compute_column_stats(
    values: List[float], col_name: str
) -> Dict[str, Any]:
    """Compute statistics for a single numeric column."""
    import statistics

    result = {
        'column': col_name,
        'count': len(values),
        'mean': round(statistics.mean(values), 2),
        'median': round(statistics.median(values), 2),
        'min': round(min(values), 2),
        'max': round(max(values), 2),
        'sum': round(sum(values), 2),
    }
    if len(values) > 1:
        result['std_dev'] = round(statistics.stdev(values), 2)
    else:
        result['std_dev'] = 0

    return result


def clear_data() -> None:
    """Clear loaded data from memory."""
    global _loaded_data
    _loaded_data = None
