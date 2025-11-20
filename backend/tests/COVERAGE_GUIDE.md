# Code Coverage Guide

## Overview

Code coverage reports are automatically generated when running tests with `./run_tests.sh`.

## Running Tests with Coverage

```bash
# Run all tests with coverage (default)
./run_tests.sh all

# Run unit tests with coverage
./run_tests.sh unit

# Run integration tests with coverage
./run_tests.sh integration

# Run tests without coverage
./run_tests.sh all --no-cov
```

## Coverage Reports Generated

### 1. Terminal Report
Shows coverage summary directly in the terminal:
- Total coverage percentage
- Coverage per file
- Missing lines highlighted

### 2. HTML Report (Detailed)
**Location:** `backend/htmlcov/index.html`

Open in your browser to see:
- Line-by-line coverage
- Which lines are covered/missing
- Branch coverage
- Interactive file browser

```bash
# Open HTML report (macOS)
open backend/htmlcov/index.html

# Or open manually in your browser
```

### 3. XML Report (CI/CD)
**Location:** `backend/coverage.xml`

Used by CI/CD tools and coverage services like:
- Codecov
- Coveralls
- GitHub Actions coverage badges

## Understanding Coverage

### Coverage Metrics

- **Statements**: Lines of code executed
- **Branches**: Conditional branches tested (if/else, try/except)
- **Missing**: Lines not covered by tests

### Good Coverage Targets

- **80%+**: Good coverage
- **90%+**: Excellent coverage
- **100%**: Complete coverage (rarely needed)

### Current Coverage

Run tests to see current coverage:
```bash
./run_tests.sh all
```

## Coverage in CI/CD

Coverage reports are generated in GitHub Actions:
- Terminal summary in CI logs
- XML report available for coverage services
- Can be uploaded to Codecov/Coveralls

## Excluding Code from Coverage

To exclude files from coverage, add to `.coveragerc` or `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
]
```

## Tips

1. **Focus on important code**: Don't obsess over 100% coverage
2. **Check HTML report**: See exactly which lines need tests
3. **Test edge cases**: Increase branch coverage
4. **Review regularly**: Run coverage before major commits

## Troubleshooting

### Coverage not showing?

Make sure pytest-cov is installed:
```bash
docker compose exec backend pip install pytest-cov
```

### HTML report not generated?

Check that the `backend/htmlcov/` directory exists and has write permissions.

### Want to see coverage for specific files?

```bash
docker compose exec backend poetry run pytest tests/ -v --cov=backend.src.application --cov-report=html
```

