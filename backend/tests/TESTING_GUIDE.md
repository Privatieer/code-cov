# Testing Guide

This guide explains how to run different types of tests in this project and how they're integrated with CI/CD.

## Test Types

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation with mocked dependencies
- **Speed**: Fast (< 1 second)
- **CI/CD**: ✅ Runs automatically in GitHub Actions
- **Marker**: `@pytest.mark.unit`

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test API endpoints with a real database (in-memory SQLite)
- **Speed**: Medium (1-5 seconds)
- **CI/CD**: ✅ Runs automatically in GitHub Actions
- **Marker**: `@pytest.mark.integration`

### 3. E2E Tests (`tests/e2e/`)
- **Purpose**: Test complete user journeys with browser automation (Playwright)
- **Speed**: Slow (10+ seconds)
- **CI/CD**: ❌ Not run in GitHub Actions (requires running services)
- **Marker**: `@pytest.mark.e2e`
- **Note**: E2E tests are **ignored by default** in `pytest.ini` to prevent accidental execution

## Running Tests

### ⚠️ Important: Python Version Compatibility

**For local testing, Docker is recommended** because:
- Python 3.13 has compatibility issues with `asyncpg` (compilation errors)
- Docker ensures consistent environment matching CI/CD
- All dependencies are pre-installed

**If running locally with Poetry:**
- Requires Python 3.11 or 3.12 (not 3.13)
- Run `poetry env use python3.11` or `poetry env use python3.12`
- Then `poetry install`

### Run All Tests (Unit + Integration)

```bash
# Using Docker (recommended - works with any Python version)
docker compose exec backend pytest tests/unit tests/integration -v

# Or locally with Poetry (requires Python 3.11 or 3.12)
cd backend
poetry env use python3.11  # or python3.12
poetry install
poetry run pytest tests/unit tests/integration -v

# Or use the helper script (handles PYTHONPATH automatically)
cd backend
./scripts/run_tests.sh all
```

### Run Only Unit Tests

```bash
# Using Docker (recommended)
docker compose exec backend pytest tests/unit -v -m unit

# Locally with Poetry (requires Python 3.11 or 3.12)
cd backend
poetry env use python3.11  # or python3.12
poetry install
poetry run pytest tests/unit -v -m unit

# Or use the helper script
cd backend
./scripts/run_tests.sh unit
```

### Run Only Integration Tests

```bash
# Using Docker (recommended)
docker compose exec backend pytest tests/integration -v -m integration

# Locally with Poetry (requires Python 3.11 or 3.12)
cd backend
poetry env use python3.11  # or python3.12
poetry install
poetry run pytest tests/integration -v -m integration

# Or use the helper script
cd backend
./scripts/run_tests.sh integration
```

### Run E2E Tests (Local Development Only)

**Prerequisites:**
1. Install Playwright:
   ```bash
   cd backend
   poetry install
   poetry run playwright install chromium
   ```

2. Start services:
   ```bash
   # Terminal 1: Start backend and dependencies
   docker compose up backend db redis
   
   # Terminal 2: Start frontend
   cd frontend
   npm install
   npm run dev
   ```

3. Run E2E tests:
   ```bash
   # Using Docker (recommended - no Python version issues)
   docker compose exec backend pytest tests/e2e -v -m e2e -o "ignore="
   
   # Or locally with Poetry (requires Python 3.11 or 3.12)
   cd backend
   poetry env use python3.11  # or python3.12
   poetry install
   poetry run pytest tests/e2e -v -m e2e -o "ignore="
   
   # Or use the helper script
   cd backend
   ./scripts/run_tests.sh e2e
   ```

**Why E2E tests are ignored by default:**
- They require frontend and backend services to be running
- They're slow and resource-intensive
- They're meant for local development and manual verification
- The `pytest.ini` has `--ignore=tests/e2e` to prevent accidental execution

## GitHub Actions CI/CD

### Current Setup

The GitHub Actions workflow (`.github/workflows/tests.yml`) automatically runs:
- ✅ Unit tests on every push/PR
- ✅ Integration tests on every push/PR
- ❌ E2E tests (not included - requires running services)

### How It Works

1. **Services**: PostgreSQL and Redis are started as GitHub Actions services
2. **Dependencies**: Poetry installs all dependencies (including dev dependencies)
3. **Test Execution**: Tests run with proper environment variables
4. **Isolation**: E2E tests are automatically ignored due to `pytest.ini` configuration

### Test Configuration

The `pytest.ini` file ensures:
- E2E tests are ignored by default (`--ignore=tests/e2e`)
- Markers are defined for filtering (`unit`, `integration`, `e2e`)
- Async mode is enabled automatically

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures for unit/integration tests
├── unit/                    # Unit tests (mocked dependencies)
│   ├── test_auth_use_case.py
│   ├── test_task_use_case.py
│   └── test_checklist_use_case.py
├── integration/             # Integration tests (real database)
│   ├── conftest.py          # Integration-specific fixtures
│   ├── test_auth_api.py
│   ├── test_tasks_api.py
│   └── test_checklists_api.py
└── e2e/                     # E2E tests (browser automation)
    ├── conftest.py          # E2E-specific fixtures (Playwright)
    ├── test_user_journey.py
    └── README.md
```

## Best Practices

1. **Always run unit/integration tests before committing**
   ```bash
   docker compose exec backend pytest tests/unit tests/integration -v
   ```

2. **Run E2E tests manually when testing complete flows**
   - Before major releases
   - When making UI changes
   - When testing authentication flows

3. **Use markers to filter tests**
   ```bash
   # Run only auth-related tests
   pytest -v -k "auth"
   
   # Run only unit tests
   pytest -v -m unit
   ```

4. **Keep tests isolated**
   - Unit tests should not depend on external services
   - Integration tests use in-memory SQLite (fast and isolated)
   - E2E tests require running services (run separately)

## Troubleshooting

### E2E Tests Not Running

If E2E tests are skipped:
- Check if Playwright is installed: `poetry run playwright --version`
- Install Playwright: `poetry run playwright install chromium`
- Ensure services are running: `docker compose ps`

### Tests Failing in CI but Passing Locally

- Check environment variables match CI configuration
- Verify database URL is correct
- Ensure all dependencies are installed

### E2E Tests Running When They Shouldn't

- Check `pytest.ini` has `--ignore=tests/e2e`
- Verify you're not overriding the ignore pattern
- Use markers: `pytest -v -m "not e2e"`

## Summary

| Test Type | CI/CD | Speed | Requires Services | How to Run |
|-----------|-------|-------|-------------------|------------|
| Unit | ✅ Yes | Fast | ❌ No | `pytest tests/unit -v -m unit` |
| Integration | ✅ Yes | Medium | ❌ No (uses in-memory DB) | `pytest tests/integration -v -m integration` |
| E2E | ❌ No | Slow | ✅ Yes | `pytest tests/e2e -v -m e2e -o "ignore="` |

The current setup ensures:
- ✅ Fast feedback in CI/CD (unit + integration tests)
- ✅ E2E tests don't break pytest flow (ignored by default)
- ✅ E2E tests can be run manually when needed
- ✅ Clear separation of concerns

