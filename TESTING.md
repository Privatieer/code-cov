# Testing Guide

This document provides an overview of the testing setup for the Task Tracker application.

## Backend Tests

### Setup

Backend tests use **pytest** with **pytest-asyncio** for async support. Tests are organized into:
- `tests/unit/` - Unit tests for business logic
- `tests/integration/` - Integration tests for API endpoints
- `tests/e2e/` - End-to-end tests (to be implemented)

### Running Backend Tests

```bash
# Run all tests
docker compose exec backend pytest

# Run unit tests only
docker compose exec backend pytest tests/unit/ -v

# Run integration tests only
docker compose exec backend pytest tests/integration/ -v

# Run with coverage
docker compose exec backend pytest --cov=backend.src --cov-report=html

# Run specific test file
docker compose exec backend pytest tests/unit/test_task_use_case.py -v

# Run tests by marker
docker compose exec backend pytest -m unit
docker compose exec backend pytest -m integration
```

### Test Coverage

#### Unit Tests
- ✅ **TaskUseCase**: Create, read, update, delete tasks
- ✅ **ChecklistUseCase**: Create/delete checklists, add/update/delete items
- ✅ **AuthUseCase**: User registration, authentication, verification

#### Integration Tests
- ✅ **Tasks API**: CRUD operations, filtering by status/priority
- ✅ **Checklists API**: CRUD operations, cascade deletion

### Test Structure

```python
@pytest.mark.unit
class TestTaskUseCase:
    @pytest.mark.asyncio
    async def test_create_task_success(self, ...):
        # Arrange
        # Act
        # Assert
```

## Frontend Tests

### Setup

Frontend tests use **Vitest** with **React Testing Library**. Configuration:
- `vitest.config.ts` - Vitest configuration
- `src/test/setup.ts` - Test setup and cleanup
- `src/test/utils.tsx` - Custom render utilities with providers

### Running Frontend Tests

```bash
# Run tests (watch mode)
cd frontend && npm run test

# Run tests with UI
cd frontend && npm run test:ui

# Run tests with coverage
cd frontend && npm run test:coverage
```

### Test Coverage

#### Component Tests
- ✅ **TasksPage**: Rendering, task display, status/priority display, checklist count

### Test Structure

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../../../test/utils';

describe('TasksPage', () => {
  it('renders tasks correctly', async () => {
    // Test implementation
  });
});
```

## Test Fixtures

### Backend Fixtures (`tests/conftest.py`)
- `db_session` - Test database session
- `mock_user_id`, `mock_task_id`, `mock_checklist_id` - Test UUIDs
- `sample_user`, `sample_task`, `sample_checklist` - Sample entities
- `mock_task_repository`, `mock_user_repository`, `mock_checklist_repository` - Mock repositories
- `mock_file_storage` - Mock file storage

### Integration Test Fixtures (`tests/integration/conftest.py`)
- `test_db_session` - Integration test database
- `test_user` - Test user in database
- `auth_token` - JWT token for authenticated requests
- `client` - Unauthenticated HTTP client
- `authenticated_client` - Authenticated HTTP client

## Best Practices

1. **Unit Tests**: Test business logic in isolation with mocked dependencies
2. **Integration Tests**: Test API endpoints with real database (in-memory SQLite)
3. **Test Isolation**: Each test should be independent and not rely on other tests
4. **Arrange-Act-Assert**: Structure tests clearly with these three sections
5. **Descriptive Names**: Use clear test names that describe what is being tested
6. **Coverage**: Aim for high coverage of critical business logic

## Next Steps

- [ ] Add E2E tests with Playwright or Cypress
- [ ] Increase frontend test coverage
- [ ] Add performance tests
- [ ] Add load tests for API endpoints
- [ ] Set up CI/CD pipeline with automated test runs

