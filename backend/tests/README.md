# Backend Tests

This directory contains unit tests, integration tests, and end-to-end tests for the backend.

## Structure

- `unit/` - Unit tests for use cases and business logic
- `integration/` - Integration tests for API endpoints
- `e2e/` - End-to-end tests (to be implemented)

## Running Tests

### Run all tests
```bash
docker compose exec backend pytest
```

### Run unit tests only
```bash
docker compose exec backend pytest tests/unit/ -v
```

### Run integration tests only
```bash
docker compose exec backend pytest tests/integration/ -v
```

### Run with coverage
```bash
docker compose exec backend pytest --cov=backend.src --cov-report=html
```

### Run specific test file
```bash
docker compose exec backend pytest tests/unit/test_task_use_case.py -v
```

### Run specific test
```bash
docker compose exec backend pytest tests/unit/test_task_use_case.py::TestTaskUseCase::test_create_task_success -v
```

## Test Markers

Tests are marked with pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests

Run tests by marker:
```bash
docker compose exec backend pytest -m unit
docker compose exec backend pytest -m integration
```

## Test Coverage

Current test coverage includes:
- ✅ TaskUseCase (create, read, update, delete)
- ✅ ChecklistUseCase (create, delete, add/update/delete items)
- ✅ AuthUseCase (register, authenticate, verify)
- ✅ Tasks API endpoints (CRUD operations, filtering)
- ✅ Checklists API endpoints (CRUD operations, cascade deletion)

