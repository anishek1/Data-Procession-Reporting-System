# DPRS Architecture

## Module Responsibilities

### core/
- `data_processor.py` — Load CSV/JSON files, compute statistics. State is encapsulated in the `DataProcessor` Singleton class; module-level functions (`load_file`, `compute_statistics`, etc.) are thin wrappers around the singleton. Return types are explicitly defined via `TypedDict` (`LoadedData`, `LoadFileResult`, `ColumnStats`).
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
- **Explicit TypedDicts** — `LoadedData`, `LoadFileResult`, `ColumnStats` replace bare `Dict[str, Any]` for type-safe return values.
- **Full in-memory load** — `rows = list(reader)` materializes all rows; lazy/chunked loading is a future backlog item since `compute_statistics()` requires a full multi-column pass.
- No external data storage (in-memory only for now)
- All errors are custom exceptions derived from `DPRSException`
- All operations logged to file + console
- Configuration centralized in `config.json`
- No external dependencies; uses Python standard library only
