# Verifying Unit and Integration Tests

This document helps verify that both unit and integration tests are properly set up.

## Test Structure

```
backend/tests/
├── unit/                    # Unit tests
│   ├── test_auth_use_case.py
│   ├── test_checklist_use_case.py
│   └── test_task_use_case.py
├── integration/            # Integration tests
│   ├── test_tasks_api.py
│   └── test_checklists_api.py
└── e2e/                    # E2E tests (optional)
    └── test_user_journey.py
```

## Unit Tests

**Location**: `backend/tests/unit/`

**Purpose**: Test individual components in isolation (use cases, domain logic)

**Characteristics**:
- Use mocks/stubs for dependencies
- Fast execution
- Test business logic only
- Marked with `@pytest.mark.unit`

**Example**: `test_auth_use_case.py`
- Tests `AuthUseCase` class methods
- Mocks `IUserRepository`
- Tests password hashing, token generation, etc.

**Run**: `pytest tests/unit -v -m unit`

## Integration Tests

**Location**: `backend/tests/integration/`

**Purpose**: Test API endpoints with real database

**Characteristics**:
- Use real database (SQLite in-memory for tests)
- Test full request/response cycle
- Test authentication, authorization
- Marked with `@pytest.mark.integration`

**Example**: `test_tasks_api.py`
- Tests `/api/v1/tasks/` endpoints
- Uses `authenticated_client` fixture
- Creates real database records
- Verifies HTTP responses

**Run**: `pytest tests/integration -v -m integration`

## Verification Checklist

### ✅ Unit Tests
- [x] Tests exist in `tests/unit/`
- [x] Tests use `@pytest.mark.unit` marker
- [x] Tests mock external dependencies
- [x] Tests are fast (< 1 second each)
- [x] Tests cover use cases and domain logic

### ✅ Integration Tests
- [x] Tests exist in `tests/integration/`
- [x] Tests use `@pytest.mark.integration` marker
- [x] Tests use real database (via `test_db_session` fixture)
- [x] Tests use `authenticated_client` fixture
- [x] Tests verify HTTP status codes and response data

### ✅ Test Configuration
- [x] `pytest.ini` configured with markers
- [x] `conftest.py` files provide fixtures
- [x] Tests can run independently
- [x] Tests clean up after themselves

## Running Tests Locally

```bash
# Run all tests
docker compose exec backend pytest

# Run only unit tests
docker compose exec backend pytest tests/unit -v -m unit

# Run only integration tests
docker compose exec backend pytest tests/integration -v -m integration

# Run both unit and integration
docker compose exec backend pytest tests/unit tests/integration -v
```

## GitHub Actions

The workflow file `.github/workflows/tests.yml` will:
1. Set up Python 3.11
2. Install Poetry and dependencies
3. Start PostgreSQL and Redis services
4. Run unit tests
5. Run integration tests
6. Report results

## Key Differences

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| **Speed** | Very fast | Slower |
| **Dependencies** | Mocked | Real (DB, etc.) |
| **Scope** | Single component | Multiple components |
| **Database** | None | SQLite in-memory |
| **HTTP** | No | Yes (via httpx) |
| **Isolation** | Complete | Per test function |

Both test types are essential:
- **Unit tests** catch logic errors early
- **Integration tests** catch integration issues

