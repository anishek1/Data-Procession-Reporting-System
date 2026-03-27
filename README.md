# DPRS — Data Processing & Reporting System

A Python data processing system with both a CLI and a REST API. Loads CSV/JSON files, validates data quality, computes statistics, generates reports, and exposes all functionality over HTTP with persistent job tracking.

## What This Project Does

- Load CSV or JSON data files (CLI and REST API)
- Validate data against defined schemas
- Clean messy data (handle missing values, type mismatches)
- Compute statistical analysis (mean, median, min, max, sum, std dev)
- Generate text and JSON reports
- Expose file upload and job status via a FastAPI REST service
- Persist job results across restarts using SQLite
- Log all operations for auditing and debugging
- Containerized with Docker for consistent deployments
- GitHub Actions CI pipeline with automated testing
- Secure logging with sensitive data redaction
- Non-root container user for security
- Dependency vulnerability scanning
- Configuration management via config.json

## Project Status

**Sprint 1: ✅ COMPLETE** — Core data processing engine, 100% test coverage

**Sprint 2: ✅ COMPLETE** — CLI interface (`load`, `summary`, `report`, `export`) and report generation

**FastAPI Feature: ✅ COMPLETE** — REST API with file upload, job tracking, SQLite persistence (`feature/fast-api-anishekh`)

**Security & Quality Hardening: ✅ COMPLETE** — traversal filenames explicitly rejected (HTTP 400), job-scoped file storage, atomic `process_file()` for concurrent-safe API uploads, atomic CRUD validation with forbidden-field set, cache-read failures logged, requirements pinned

**Sprint 3: ✅ COMPLETE** — Docker, GitHub Actions CI/CD

See `PROJECT_STATE.md` for detailed progress.

## Quick Start

### Prerequisites
- Python 3.9+
- Git
- pip (comes with Python)

### Clone the Repository

```bash
# Clone from main branch
git clone https://github.com/your-username/dprs.git
cd dprs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=core --cov=utils --cov=api tests/ -v

# Expected: 56/56 tests passing
```

### Use the CLI

```bash
python cli/main.py load --file input/weight-height.csv
python cli/main.py summary
python cli/main.py report --type text
python cli/main.py export --format json
```

### Use the REST API

```bash
uvicorn api.main:app --reload
# Interactive docs: http://127.0.0.1:8000/docs
```

```bash
# Upload a file
curl -X POST http://127.0.0.1:8000/upload -F "file=@input/weight-height.csv"
# Returns: { "job_id": "...", "status": "completed", "statistics": { ... } }

# Retrieve results by job ID
curl http://127.0.0.1:8000/jobs/<job_id>
```
### Run via Docker

#### Prerequisites
- Docker Desktop installed and running

#### Build the Image
```bash
docker build -t dprs-app .
```

#### Run the REST API
```bash
docker run -p 8000:8000 dprs-app
```
Then open **http://127.0.0.1:8000/docs** in your browser for the interactive API docs.

#### Run the CLI via Docker
```bash
# Load a file
docker run -v ${PWD}:/app dprs-app load --file input/weight-height.csv

# Get summary
docker run -v ${PWD}:/app dprs-app summary

# Generate report
docker run -v ${PWD}:/app dprs-app report --type text

# Export JSON
docker run -v ${PWD}:/app dprs-app export --format json
```
#### Upload a File via Docker API
```bash
curl -X POST http://127.0.0.1:8000/upload -F "file=@input/weight-height.csv"
```


## Project Structure

```text
dprs/
├── core/                    # Data processing engine ✅
│   ├── data_processor.py    # DataProcessor Singleton — load files, compute statistics
│   ├── validator.py         # Schema validation, data cleaning
│   └── exceptions.py        # Custom exception hierarchy
│
├── utils/                   # Utilities ✅
│   ├── logger.py            # Logging with file rotation
│   └── config.py            # config.json management
│
├── api/                     # REST API ✅
│   ├── main.py              # FastAPI app, startup
│   ├── models.py            # Pydantic response models
│   ├── database.py          # SQLAlchemy engine & session
│   ├── db_models.py         # Job ORM model (jobs table)
│   ├── crud.py              # create_job, update_job, get_job
│   └── routes/
│       ├── upload.py        # POST /upload
│       └── jobs.py          # GET /jobs/{job_id}
│
├── reporting/               # Report generation ✅
│   └── report_generator.py
│
├── cli/                     # CLI interface ✅
│   └── main.py
│
├── tests/                   # Tests ✅ (53 passing)
│
├── input/                   # Data files
├── output/                  # Generated reports
├── logs/                    # Application logs
├── dprs.db                  # SQLite database (auto-created)
├── config.json              # Configuration
├── Dockerfile               # Container configuration
├── .github/
│   └── workflows/
│       └── test.yml         # CI/CD pipeline
└── requirements.txt         # Dependencies
```

## Development Workflow

### For Team Members — How to Contribute

We use **feature branches** to keep work organized and prevent conflicts.

#### Naming Convention

```
data-processing-engineer    ← Intern 1's branch (Sprint 1 - COMPLETE)
feature/sprint-2-cli        ← Intern 2's branch (Sprint 2)
feature/anirudh     ← Intern 3's branch (Sprint 3)
```

#### Workflow for Each Sprint

**Step 1: Create Your Feature Branch**

```bash
# Start from main
git checkout main
git pull origin main

# Create your feature branch
git checkout -b feature/sprint-2-cli   # Example for Intern 2

# Or for a more descriptive name:
git checkout -b feature/sprint-2-cli-interface-and-reporting
```

**Step 2: Do Your Work**

```bash
# Make changes, test locally
python -m pytest tests/ -v

# Commit your work with clear messages
git add .
git commit -m "Sprint 2: Implement load command"
git commit -m "Sprint 2: Add report generation"
```

**Step 3: Push to GitHub**

```bash
# Push your feature branch
git push -u origin feature/sprint-2-cli
```

**Step 4: Create Pull Request**

- Go to GitHub
- Switch to your feature branch
- Click "Compare & pull request"
- Add description: "Sprint 2: CLI interface and report generation"
- Request code review from team

**Step 5: Code Review & Merge**

- Team reviews your code
- Fix any feedback
- Once approved, merge to main
- Delete feature branch

### Using Completed Modules

The core data processing module (`data-processing-engineer` branch) is complete. You can:

**Option A: Clone from main (Recommended)**
```bash
git clone https://github.com/your-username/dprs.git
cd dprs

# main branch already has the merged core module
# You'll build on top of it
```

**Option B: Clone from feature branch (If main not updated yet)**
```bash
git clone --branch data-processing-engineer https://github.com/your-username/dprs.git
cd dprs

# You have the core module code
# Create your own feature branch from here
git checkout -b feature/sprint-2-cli
```

**Why Option A is better:** Keep main as single source of truth. Once each sprint is complete, merge feature branch → main. Next developer starts from main with everything so far.

## Code Quality Standards

All code follows these standards:

- **Style:** PEP 8 (Python style guide)
- **Documentation:** 100% docstring coverage
- **Comments:** Complex logic has inline comments
- **Testing:** minimum 85% code coverage; aspirational target 100%
- **Logging:** All operations logged, no print statements
- **Configuration:** All settings in config.json, no hardcoding

### Running Code Quality Checks

```bash
# Check PEP 8 style (if flake8 installed)
flake8 dprs/

# Run tests with coverage
pytest --cov=core --cov=utils tests/ -v

# Expected output: 56/56 tests passing, ≥85% coverage (target: 100%)
```

## Configuration

Edit `config.json` to customize:

```json
{
    "app": {
        "name": "DPRS",
        "version": "1.0.0",
        "environment": "development"
    },
    "logging": {
        "level": "INFO",
        "file": "logs/app.log",
        "max_bytes": 10485760,
        "backup_count": 7
    },
    "data": {
        "input_dir": "input",
        "output_dir": "output",
        "sample_csv": "input/sample_data.csv",
        "sample_json": "input/sample_data.json",
        "schema_validation": true
    },
    "reporting": {
        "default_format": "text",
        "save_to_file": true,
        "report_dir": "output/reports"
    }
}
```

## Testing

All modules are thoroughly tested:

| Module | Tests |
|--------|-------|
| data_processor.py | 10 |
| validator.py | 11 |
| config.py | 6 |
| logger.py | 5 |
| cli/main.py | 5 |
| report_generator.py | 4 |
| API (upload, jobs, health) | 12 |
| **TOTAL** | **56** |

Run all tests:
```bash
pytest tests/ -v
```

## Troubleshooting

**ModuleNotFoundError?**
- Make sure virtual environment is activated
- Check that all `__init__.py` files exist in core/, utils/, tests/

**Tests won't run?**
- Install pytest: `pip install pytest pytest-cov`
- Run from project root: `pytest tests/`

**Configuration not loading?**
- Ensure config.json is in the root directory
- Check JSON is valid: `python -m json.tool config.json`

**Import errors?**
- Verify you're in the `dprs/` directory
- Check that __pycache__ is deleted (can cause stale imports)

## Team Information

| Role | Focus Area | Sprint | Branch |
|------|-----------|--------|--------|
| Intern 1 | Data Processing | Sprint 1 ✅ | data-processing-engineer |
| Intern 2 | CLI & Reporting | Sprint 2 | feature/sprint-2-cli |
| Intern 3 | DevOps | Sprint 3 | feature/anirudh |

## Key Decisions & Architecture

**Why Pure Python (No numpy/pandas)?**
- Keeps dependencies minimal
- Suitable for current dataset sizes (≤100k rows)
- Can refactor to numpy/pandas if performance needed
- Makes code easier to understand and maintain

**Why In-Memory for Processing, SQLite for Jobs?**
- CSV/JSON data loaded in memory for fast processing (≤100k rows); state is managed by the `DataProcessor` Singleton class, not a bare global variable
- Job metadata (id, status, statistics, timestamps) persisted to SQLite via SQLAlchemy
- SQLite needs no external server — single `dprs.db` file, zero config
- `database_url` in `config.json` allows swapping to PostgreSQL/MySQL later

**Why Custom Exceptions?**
- Consistent error handling across modules
- Better control over error messages
- Makes debugging easier

**Why Config-Driven Design?**
- Different settings per environment
- No code changes needed for deployments
- All configuration in one place

See `ARCHITECTURE.md` for more details.

## Git Workflow Summary

```
main (production code)
  ↑
  └─ Pull Request ← code review
       ↑
       └─ feature/sprint-2-cli
       └─ feature/sprint-3-devops
       └─ data-processing-engineer (merged after Sprint 1)
```

Each sprint:
1. Create feature branch from main
2. Do your work, test thoroughly
3. Push to GitHub
4. Create Pull Request
5. Team reviews
6. Merge to main
7. Delete feature branch

## Next Steps

- **Anishekh:** PR `#8` opened (`feature/fast-api-anishekh` → main) — awaiting team review
- **Anirudh:**: implement secure file handling and dependency vulnerability scanning 
- **Team:** Review and merge FastAPI branch, daily standups

See `PROJECT_STATE.md` for detailed sprint progress.

## Documentation

- `ARCHITECTURE.md` — Module design and responsibilities
- `PROJECT_STATE.md` — Current progress and status
- `config.json` — Configuration template


