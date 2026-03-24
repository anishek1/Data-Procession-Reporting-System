# DPRS Architecture

## Module Responsibilities

### core/
- `data_processor.py` — Load CSV/JSON files, compute statistics. State is encapsulated in the `DataProcessor` Singleton class; module-level functions (`load_file`, `compute_statistics`, `process_file`, etc.) are thin wrappers around the singleton. `process_file()` loads and computes atomically into a local variable without mutating the Singleton's shared state — safe for concurrent API requests. Return types are explicitly defined via `TypedDict` (`LoadedData`, `LoadFileResult`, `ColumnStats`).
- `validator.py` — Validate schema, check required fields, verify data types
- `exceptions.py` — Custom exception hierarchy for all error handling

### reporting/
- `report_generator.py` — Format data into text reports, JSON exports

### cli/
- `main.py` — Command-line interface, argument parsing, command routing

### utils/
- `logger.py` — Centralized logging setup with file rotation
- `config.py` — Load configuration from config.json

## Data Flow

1. CLI receives command from user
2. CLI calls appropriate module (data_processor, report_generator, etc.)
3. `data_processor.load_file()` reads and parses file
4. `validator.validate_schema()` checks structure
5. Processed data stored in memory
6. Statistics computed and formatted
7. `report_generator` creates text/JSON output
8. Results written to `output/` directory
9. All operations logged to `logs/app.log`

## Dependencies Between Modules

- `cli/main.py` depends on: `core/`, `reporting/`, `utils/`
- `core/data_processor.py` depends on: `core/validator`, `core/exceptions`, `utils/logger`
- `core/validator.py` depends on: `core/exceptions`, `utils/logger`
- `reporting/report_generator.py` depends on: `utils/logger`
- All modules use: `utils/config` for configuration

## Key Decisions

- **Singleton for state** — `DataProcessor` uses `__new__` Singleton pattern (same as `utils/config.py`'s `get_config()`). Eliminates module-level global variables while keeping the public API identical.
- **Atomic API processing** — `process_file()` loads a file and computes statistics entirely from a local variable, never touching `self._data`. This keeps concurrent API requests safe without locks; the CLI flow (`load_file` + `compute_statistics`) is unchanged.
- **Explicit TypedDicts** — `LoadedData`, `LoadFileResult`, `ColumnStats` replace bare `Dict[str, Any]` for type-safe return values.
- **Full in-memory load** — `rows = list(reader)` materializes all rows; lazy/chunked loading is a future backlog item since `compute_statistics()` requires a full multi-column pass.
- No external data storage (in-memory only for now)
- All errors are custom exceptions derived from `DPRSException`; all re-raises use `raise ... from e` to preserve the original traceback
- All operations logged to file + console; cache-write and cache-read failures in `data_processor.py` are logged at DEBUG level (with `exc_info=True` for reads) rather than silently ignored
- Configuration centralized in `config.json`
- No external dependencies in the core processing layer; API layer uses FastAPI, SQLAlchemy, uvicorn, python-multipart (all pinned with `>=min,<next_major` bounds in `requirements.txt`)

## Security & Robustness

- **Path traversal rejection** — `api/routes/upload.py` explicitly rejects filenames containing `..`, `/`, or `\` (HTTP 400) before any job record is created. This prevents orphaned DB rows on rejected uploads and makes the security boundary explicit and testable.
- **Job-scoped file storage** — uploaded files are written as `{job_id}_{safe_filename}` under `input/`, preventing collisions when concurrent jobs upload files with the same basename.
- **Atomic CRUD validation** — `api/crud.update_job` computes `allowed_columns = valid_columns - forbidden_fields` (where `forbidden_fields = {"job_id", "created_at"}`), validates all keys in one pass before any `setattr` call, and raises a single `ValueError` listing every bad key. This prevents partial ORM mutations and blocks writes to immutable columns.
- **Broad exception handling in upload** — the processing block in `POST /upload` catches `Exception` (not only `DPRSException | ValueError`) so unexpected runtime errors also mark the job `failed` and surface HTTP 422, rather than leaving the job stuck in `processing` state.
