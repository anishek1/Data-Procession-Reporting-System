# DPRS — Data Processing & Reporting System

A Python CLI application for processing structured data files (CSV/JSON), validating data quality, computing statistics, and generating reports. Built with clean architecture principles and full test coverage.

## What It Does

- **Load data** from CSV or JSON files
- **Validate** data against defined schemas
- **Clean** messy data (handle missing values, type mismatches)
- **Analyze** with statistics (mean, median, min, max, etc.)
- **Report** results in text or JSON format
- **Log** everything for debugging and auditing

## Quick Start

### Prerequisites
- Python 3.9+
- pip (comes with Python)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/anishek1/Data-Procession-Reporting-System.git
cd dprs

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies (pytest for tests)
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v
pytest --cov=core --cov=utils tests/  # Run with coverage
```

### Use the System

We're currently in active development. The CLI interface is coming in Sprint 2.

For now, you can import and use the modules directly in a Python script or shell:

```python
from core.data_processor import load_file, compute_statistics
from core.validator import Schema, validate_schema

# Load your data
result = load_file("input/sample_data.csv")

# Compute statistics
stats = compute_statistics()

print(stats)
```

## Project Structure

```
dprs/
├── core/              # Data processing logic
│   ├── data_processor.py    # Load files, compute stats
│   ├── validator.py         # Schema validation
│   └── exceptions.py        # Custom exceptions
├── reporting/         # Report generation (coming Sprint 2)
├── cli/               # CLI interface (coming Sprint 2)
├── utils/             # Logging & config
│   ├── logger.py
│   └── config.py
├── tests/             # Unit tests
├── input/             # Sample data files
├── output/            # Generated reports
├── logs/              # Application logs
└── config.json        # Configuration
```

## Development Status

**Sprint 1 ✅ Complete**
- Core data processing module implemented
- File loading (CSV/JSON) working
- Schema validation complete
- Data cleaning functional
- Statistics computation ready
- Full test coverage (87%)

**Next: Sprint 2**
- CLI interface
- Report generation
- Integration testing

See `PROJECT_STATE.md` for detailed progress.

## Testing

All code has unit tests. Our test coverage target is ≥80%.

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_processor.py -v

# Show coverage report
pytest --cov=core --cov=utils tests/
```

## Contributing

This is a team project. Make sure you're working on the `dev` branch, not `main`.

```bash
# Get the latest dev branch
git checkout dev
git pull origin dev

# Make your changes, then:
git add .
git commit -m "Brief description of changes"
git push origin dev
```

## Configuration

You can edit `config.json` to change:
- Log level (INFO, DEBUG, WARNING, ERROR)
- Log file location
- Input/output directories

## Troubleshooting

**ModuleNotFoundError?**
- Ensure you're in the `dprs/` directory when running Python commands
- Check that all `__init__.py` files exist in `core/`, `utils/`, `tests/`
- Is your `venv` active?

**Tests won't run?**
- Did you `pip install pytest pytest-cov`?
- Are you running it from the root `dprs/` directory?

**Import errors?**
- Make sure virtual environment is activated: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

## Team

- Intern 1: Data Processing Module (Sprint 1 ✅)
- Intern 2: CLI & Reporting (Sprint 2 — in progress)
- Intern 3: DevOps & Utilities (Sprint 3 — coming)

## License

[MIT License]
