# DPRS — Data Processing & Reporting System

A Python CLI application for processing structured data (CSV/JSON), validating quality, computing statistics, and generating reports. Built with clean architecture and comprehensive testing.

## What This Project Does

- Load CSV or JSON data files
- Validate data against defined schemas
- Clean messy data (handle missing values, type mismatches)
- Compute statistical analysis (mean, median, min, max, sum, std dev)
- Generate text and JSON reports
- Log all operations for auditing and debugging

## Project Status

**Sprint 1: ✅ COMPLETE**
- Core data processing module fully implemented
- 35 unit tests, 100% code coverage
- Production-ready code on `data-processing-engineer` branch
- Ready for integration with CLI (Sprint 2)

**Sprint 2: 🔄 IN PROGRESS**
- Intern 2 building CLI interface and report generation

**Sprint 3: ⏳ UPCOMING**
- Intern 3 handling Docker and GitHub Actions

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
pytest --cov=core --cov=utils tests/ -v

# Expected: 35/35 tests passing, 100% coverage
```

### Use the Core Module

The core data processing engine is fully functional:

```python
from dprs.core.data_processor import load_file, compute_statistics
from dprs.core.validator import Schema, validate_schema

# Load data
result = load_file("input/sales.csv")
print(f"Loaded {result['rows']} rows, {result['columns']} columns")

# Compute statistics
stats = compute_statistics()
print(stats)
```

## Project Structure

```
dprs/
├── core/                    # Data processing engine (COMPLETE ✅)
│   ├── data_processor.py    # Load files, compute statistics
│   ├── validator.py         # Schema validation, data cleaning
│   └── exceptions.py        # Custom exception classes
│
├── utils/                   # Utilities (COMPLETE ✅)
│   ├── logger.py            # Logging setup with rotation
│   └── config.py            # Configuration management
│
├── reporting/               # Report generation (IN PROGRESS)
│   └── report_generator.py
│
├── cli/                     # CLI interface (IN PROGRESS)
│   └── main.py
│
├── tests/                   # Unit tests (COMPLETE ✅)
│   ├── test_processor.py
│   ├── test_validator.py
│   ├── test_config.py
│   └── test_logger.py
│
├── input/                   # Sample data files
├── output/                  # Generated reports
├── logs/                    # Application logs
├── config.json              # Configuration
└── requirements.txt         # Dependencies
```

## Development Workflow

### For Team Members — How to Contribute

We use **feature branches** to keep work organized and prevent conflicts.

#### Naming Convention

```
data-processing-engineer    ← Intern 1's branch (Sprint 1 - COMPLETE)
feature/sprint-2-cli        ← Intern 2's branch (Sprint 2)
feature/sprint-3-devops     ← Intern 3's branch (Sprint 3)
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
- **Testing:** ≥85% code coverage (our target: 100%)
- **Logging:** All operations logged, no print statements
- **Configuration:** All settings in config.json, no hardcoding

### Running Code Quality Checks

```bash
# Check PEP 8 style (if flake8 installed)
flake8 dprs/

# Run tests with coverage
pytest --cov=core --cov=utils tests/ -v

# Expected output: 35/35 tests passing, 100% coverage
```

## Configuration

Edit `config.json` to customize:

```json
{
  "log_level": "INFO",        # Logging level
  "log_file": "logs/app.log",
  "input_dir": "input",       # Where to load data from
  "output_dir": "output"      # Where to save reports
}
```

## Testing

All modules are thoroughly tested:

| Module | Tests | Coverage |
|--------|-------|----------|
| data_processor.py | 6 | 100% |
| validator.py | 5 | 100% |
| config.py | 4 | 100% |
| logger.py | 4 | 100% |
| Other | 16+ | 100% |
| **TOTAL** | **35+** | **100%** |

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
| Intern 3 | DevOps | Sprint 3 | feature/sprint-3-devops |

## Key Decisions & Architecture

**Why Pure Python (No numpy/pandas)?**
- Keeps dependencies minimal
- Suitable for current dataset sizes (≤100k rows)
- Can refactor to numpy/pandas if performance needed
- Makes code easier to understand and maintain

**Why In-Memory Storage?**
- Simpler for initial development
- Works well for typical use cases
- Can migrate to database later if needed

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

- **Intern 2:** Start Sprint 2 (CLI interface)
- **Intern 3:** Start Sprint 3 (Docker & DevOps)
- **Team:** Daily standups, code reviews before merge

See `PROJECT_STATE.md` for detailed sprint progress.

## Documentation

- `ARCHITECTURE.md` — Module design and responsibilities
- `PROJECT_STATE.md` — Current progress and status
- `config.json` — Configuration template

## License

[Your License Here]

---

*Last updated: [Today's Date]*
