# Testing Setup Guide

This document describes the complete testing infrastructure for the Task Tracker application.

## Test Types

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Run**: `pytest tests/unit -v`
- **Coverage**: Tests use cases, domain logic, and business rules
- **Examples**: `test_auth_use_case.py`, `test_task_use_case.py`

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test API endpoints with real database (SQLite in-memory)
- **Run**: `pytest tests/integration -v`
- **Coverage**: Tests API routes, database interactions, authentication
- **Examples**: `test_tasks_api.py`, `test_checklists_api.py`

### 3. E2E Tests (`tests/e2e/`)
- **Purpose**: Test complete user journeys using Playwright
- **Run**: `pytest tests/e2e -v -m e2e`
- **Coverage**: Tests full user workflows from frontend to backend
- **Examples**: `test_user_journey.py`

## Running Tests

### All Tests
```bash
cd backend
poetry run pytest -v
```

### With Coverage
```bash
poetry run pytest --cov=backend.src --cov-report=html --cov-report=term
```

### Specific Test Types
```bash
# Unit tests only
poetry run pytest tests/unit -v

# Integration tests only
poetry run pytest tests/integration -v

# E2E tests only (requires frontend running)
poetry run pytest tests/e2e -v -m e2e
```

### Coverage Report
After running tests with coverage, open `htmlcov/index.html` in your browser.

## E2E Testing Setup

### Prerequisites
1. Install Playwright browsers:
```bash
cd backend
poetry run playwright install chromium
```

2. Start the application:
```bash
# Terminal 1: Start backend and services
docker-compose up backend db redis

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

### Running E2E Tests
```bash
cd backend
FRONTEND_URL=http://localhost:3000 BACKEND_URL=http://localhost:8004 \
poetry run pytest tests/e2e -v -m e2e
```

## Code Coverage

### Configuration
- Coverage threshold: **70%** (configurable in `pytest.ini`)
- Coverage reports: HTML, XML, Terminal
- Coverage configuration: `backend/.coveragerc`

### Viewing Coverage
```bash
# Generate HTML report
poetry run pytest --cov=backend.src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## CI/CD Integration

### GitHub Actions
Workflow file: `.github/workflows/ci.yml`

**Features:**
- Runs unit, integration, and E2E tests
- Generates coverage reports
- Uploads coverage to Codecov
- Comments PRs with coverage information
- Artifacts: HTML coverage reports, test results

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

### GitLab CI
Workflow file: `.gitlab-ci.yml`

**Features:**
- Runs all test types
- Generates coverage reports
- Coverage badges in merge requests

## Test Markers

Tests are organized using pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests

Run specific markers:
```bash
pytest -m unit
pytest -m integration
pytest -m e2e
```

## Best Practices

### Writing E2E Tests
1. Use descriptive test names that explain the user journey
2. Use `page` fixture for browser interactions
3. Use `api_client` for direct API verification
4. Wait for elements with appropriate timeouts
5. Clean up test data after tests

### Writing Integration Tests
1. Use `authenticated_client` fixture for authenticated requests
2. Create test data in fixtures
3. Clean up after tests (handled automatically)
4. Test both success and error cases

### Writing Unit Tests
1. Mock external dependencies
2. Test one thing per test
3. Use descriptive assertions
4. Test edge cases and error conditions

## Troubleshooting

### E2E Tests Failing
1. Ensure frontend is running on `http://localhost:3000`
2. Ensure backend is running on `http://localhost:8004`
3. Check browser console for errors
4. Increase timeouts if needed

### Coverage Not Generating
1. Ensure `pytest-cov` is installed: `poetry add --group dev pytest-cov`
2. Check `.coveragerc` configuration
3. Verify source paths are correct

### CI/CD Failures
1. Check GitHub Actions/GitLab CI logs
2. Verify environment variables are set
3. Ensure services (Postgres, Redis) are available
4. Check test timeout settings

## Next Steps

1. **Increase Coverage**: Aim for 80%+ coverage
2. **Add More E2E Tests**: Cover all major user journeys
3. **Performance Tests**: Add load testing for critical endpoints
4. **Visual Regression**: Consider adding visual regression testing
5. **Accessibility Tests**: Add a11y testing to E2E suite

