"""
Data Processing Module

Handles file loading, data parsing, and statistical calculations.
Supports CSV and JSON formats.

State is managed by the DataProcessor Singleton class. Module-level
functions are thin wrappers that delegate to the singleton instance,
preserving the existing public API for all callers.
"""

import csv
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, TypedDict
from .exceptions import FileNotFoundError as DPRSFileNotFoundError
from .exceptions import InvalidFileTypeError
from utils.logger import logger


# ---------------------------------------------------------------------------
# Explicit return-type definitions
# ---------------------------------------------------------------------------

class LoadedData(TypedDict):
    """Internal representation of a loaded dataset."""
    headers: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    column_count: int


class LoadFileResult(TypedDict):
    """Return value of load_file()."""
    status: str
    file: str
    rows: int
    columns: int
    headers: List[str]


class ColumnStats(TypedDict):
    """Statistics for a single numeric column."""
    column: str
    count: int
    mean: float
    median: float
    min: float
    max: float
    sum: float
    std_dev: float


# ---------------------------------------------------------------------------
# DataProcessor Singleton
# ---------------------------------------------------------------------------

class DataProcessor:
    """
    Encapsulates data loading, caching, and statistical computation.

    Implemented as a Singleton so that all callers share one in-memory
    dataset without relying on module-level global variables.  Access via
    ``DataProcessor()`` (or the private ``_get_processor()`` helper below).

    The Singleton instance is never destroyed; only its ``_data`` attribute
    is zeroed by ``clear()``.  This keeps the public API identical to the
    previous global-variable implementation while eliminating ``global``
    keyword usage throughout the module.
    """

    _instance: Optional['DataProcessor'] = None

    def __new__(cls) -> 'DataProcessor':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = None  # initialise only on first construction
        return cls._instance

    # ------------------------------------------------------------------
    # Private loading helpers
    # ------------------------------------------------------------------

    def _load_csv(self, filepath: str) -> LoadedData:
        """
        Load a CSV file and return structured data.

        Args:
            filepath: Path to CSV file

        Returns:
            LoadedData with 'headers', 'rows', 'row_count', 'column_count'

        Raises:
            DPRSFileNotFoundError: If file doesn't exist
            InvalidFileTypeError: If file is not CSV
        """
        path = Path(filepath)

        if not path.exists():
            raise DPRSFileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != '.csv':
            raise InvalidFileTypeError(
                f"Expected .csv file, got {path.suffix}"
            )

        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = list(reader.fieldnames) if reader.fieldnames else []
                # NOTE: full materialization required for multi-column statistics pass.
                # Lazy/chunked loading is a future optimization (requires stats-during-load
                # redesign).
                rows = list(reader)

            return LoadedData(
                headers=headers,
                rows=rows,
                row_count=len(rows),
                column_count=len(headers),
            )
        except Exception as e:
            raise DPRSFileNotFoundError(f"Error reading CSV file: {str(e)}") from e

    def _load_json(self, filepath: str) -> LoadedData:
        """
        Load a JSON file (array of objects format).

        Args:
            filepath: Path to JSON file

        Returns:
            LoadedData with 'headers', 'rows', 'row_count', 'column_count'

        Raises:
            DPRSFileNotFoundError: If file doesn't exist
            InvalidFileTypeError: If file is not JSON or has wrong format
        """
        path = Path(filepath)

        if not path.exists():
            raise DPRSFileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != '.json':
            raise InvalidFileTypeError(
                f"Expected .json file, got {path.suffix}"
            )

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON must be an array of objects")

            if len(data) == 0:
                return LoadedData(
                    headers=[],
                    rows=[],
                    row_count=0,
                    column_count=0,
                )

            headers = list(data[0].keys())
            return LoadedData(
                headers=headers,
                rows=data,
                row_count=len(data),
                column_count=len(headers),
            )
        except json.JSONDecodeError as e:
            raise InvalidFileTypeError(f"Invalid JSON format: {str(e)}") from e
        except (FileNotFoundError, PermissionError, OSError) as e:
            raise DPRSFileNotFoundError(f"Error reading JSON file: {str(e)}") from e

    def _compute_column_stats(
        self, values: List[float], col_name: str
    ) -> ColumnStats:
        """Compute statistics for a single numeric column."""
        result = ColumnStats(
            column=col_name,
            count=len(values),
            mean=round(statistics.mean(values), 2),
            median=round(statistics.median(values), 2),
            min=round(min(values), 2),
            max=round(max(values), 2),
            sum=round(sum(values), 2),
            std_dev=round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        )
        return result

    def _compute_stats_from_data(
        self, data: LoadedData, column_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute statistics from a provided LoadedData object (no self._data access).

        Extracted so that process_file() can compute stats without touching shared
        singleton state, making concurrent API requests safe.
        """
        rows = data['rows']
        headers = data['headers']

        if len(rows) == 0:
            return {'error': 'No data rows to process'}

        stats: Dict[str, Any] = {}
        columns_to_process = [column_name] if column_name else headers

        for col in columns_to_process:
            if col not in headers:
                stats[col] = {'error': f"Column '{col}' not found"}
                continue

            numeric_values: List[float] = []
            for row in rows:
                val = row.get(col)
                if val is not None and val != '':
                    try:
                        numeric_values.append(float(val))
                    except (ValueError, TypeError):
                        pass

            if numeric_values:
                stats[col] = self._compute_column_stats(numeric_values, col)

        return stats

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def load_file(self, filepath: str) -> LoadFileResult:
        """
        Load a data file (CSV or JSON) based on file extension.
        Stores data in instance memory for later processing.

        Args:
            filepath: Path to CSV or JSON file

        Returns:
            LoadFileResult with status, file path, row/column counts, and headers

        Raises:
            DPRSFileNotFoundError: If file doesn't exist
            InvalidFileTypeError: If format not supported
        """
        path = Path(filepath)

        if path.suffix.lower() == '.csv':
            data = self._load_csv(str(path))
        elif path.suffix.lower() == '.json':
            data = self._load_json(str(path))
        else:
            raise InvalidFileTypeError(
                f"Unsupported file format: {path.suffix}. Use .csv or .json"
            )

        self._data = data

        # Persist to cache for stateless CLI workflows
        try:
            with open('.dprs_cache.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logger.debug(f"Could not write cache file: {e}")

        return LoadFileResult(
            status='success',
            file=str(path),
            rows=data['row_count'],
            columns=data['column_count'],
            headers=data['headers'],
        )

    def get_loaded_data(self) -> Optional[LoadedData]:
        """Get the currently loaded data from memory."""
        return self._data

    def compute_statistics(
        self, column_name: Optional[str] = None
    ) -> Dict[str, Any]:
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
        if self._data is None:
            # Try to retrieve from disk cache for CLI state persistence
            cache_path = Path('.dprs_cache.json')
            if cache_path.exists():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        self._data = json.load(f)
                except Exception as e:
                    logger.debug(
                        f"Could not read cache file {cache_path}: {e}", exc_info=True
                    )

        if self._data is None:
            raise ValueError("No data loaded. Call load_file() first.")

        return self._compute_stats_from_data(self._data, column_name)

    def load_csv(self, filepath: str) -> LoadedData:
        """
        Load a CSV file, update internal state, and persist the disk cache.

        Mirrors load_file() for CSV specifically, so callers can use
        compute_statistics() after calling this method.
        """
        data = self._load_csv(filepath)
        self._data = data
        try:
            with open('.dprs_cache.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logger.debug(f"Could not write cache file: {e}")
        return data

    def load_json(self, filepath: str) -> LoadedData:
        """
        Load a JSON file, update internal state, and persist the disk cache.

        Mirrors load_file() for JSON specifically, so callers can use
        compute_statistics() after calling this method.
        """
        data = self._load_json(filepath)
        self._data = data
        try:
            with open('.dprs_cache.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logger.debug(f"Could not write cache file: {e}")
        return data

    def clear(self) -> None:
        """
        Clear loaded data from memory and remove the disk cache.

        Zeros ``_data`` on the live Singleton instance without destroying
        the instance itself, so all existing references remain valid.
        """
        self._data = None
        cache_path = Path('.dprs_cache.json')
        if cache_path.exists():
            cache_path.unlink()

    def process_file(
        self, filepath: str
    ) -> Tuple[LoadFileResult, Dict[str, Any]]:
        """Load a file and compute statistics atomically without touching self._data.

        Designed for the API upload flow where concurrent requests must not
        interleave through the shared singleton state. The result is derived
        entirely from a local variable; self._data is never read or written.

        Args:
            filepath: Path to a CSV or JSON file.

        Returns:
            A (LoadFileResult, stats_dict) tuple.

        Raises:
            DPRSFileNotFoundError: If file doesn't exist.
            InvalidFileTypeError: If format not supported.
        """
        path = Path(filepath)

        if path.suffix.lower() == '.csv':
            data = self._load_csv(str(path))
        elif path.suffix.lower() == '.json':
            data = self._load_json(str(path))
        else:
            raise InvalidFileTypeError(
                f"Unsupported file format: {path.suffix}. Use .csv or .json"
            )

        stats = self._compute_stats_from_data(data)

        file_meta = LoadFileResult(
            status='success',
            file=str(path),
            rows=data['row_count'],
            columns=data['column_count'],
            headers=data['headers'],
        )

        return file_meta, stats


# ---------------------------------------------------------------------------
# Module-level public API (thin wrappers — signatures are unchanged)
# ---------------------------------------------------------------------------

def _get_processor() -> DataProcessor:
    """Return the DataProcessor Singleton instance."""
    return DataProcessor()


def load_file(filepath: str) -> LoadFileResult:
    """
    Load a data file (CSV or JSON) based on file extension.
    Delegates to DataProcessor singleton.
    """
    return _get_processor().load_file(filepath)


def load_csv(filepath: str) -> LoadedData:
    """
    Load a CSV file, update singleton state, and return structured data.
    Delegates to DataProcessor singleton.
    """
    return _get_processor().load_csv(filepath)


def load_json(filepath: str) -> LoadedData:
    """
    Load a JSON file (array of objects format), update singleton state, and return structured data.
    Delegates to DataProcessor singleton.
    """
    return _get_processor().load_json(filepath)


def get_loaded_data() -> Optional[LoadedData]:
    """Get the currently loaded data from memory. Delegates to DataProcessor singleton."""
    return _get_processor().get_loaded_data()


def compute_statistics(column_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute statistical summary of loaded data.
    Delegates to DataProcessor singleton.
    """
    return _get_processor().compute_statistics(column_name)


def clear_data() -> None:
    """Clear loaded data from memory and remove the disk cache.
    Delegates to DataProcessor singleton."""
    _get_processor().clear()


def process_file(
    filepath: str,
) -> Tuple[LoadFileResult, Dict[str, Any]]:
    """Load a file and compute statistics atomically without touching shared state.

    Designed for the API upload flow. Does not modify the singleton's _data.
    Delegates to DataProcessor.process_file().
    """
    return _get_processor().process_file(filepath)
