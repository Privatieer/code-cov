# E2E Tests

End-to-end tests using Playwright to simulate real user interactions with the application.

## Prerequisites

1. Install dependencies:
```bash
cd backend
poetry install
poetry run playwright install chromium
```

2. Ensure the application is running:
```bash
# Terminal 1: Start backend
docker-compose up backend db redis

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

## Running E2E Tests

### Run all E2E tests:
```bash
cd backend
poetry run pytest tests/e2e -v -m e2e
```

### Run specific test:
```bash
poetry run pytest tests/e2e/test_user_journey.py::TestUserJourney::test_complete_user_registration_and_task_management -v
```

### Run with coverage:
```bash
poetry run pytest tests/e2e -v -m e2e --cov=backend.src --cov-report=html
```

## Environment Variables

- `FRONTEND_URL`: Frontend URL (default: http://localhost:3000)
- `BACKEND_URL`: Backend URL (default: http://localhost:8004)
- `TESTING`: Set to "true" to disable rate limiting

## Test Structure

- `conftest.py`: Fixtures for browser, page, database, and API client
- `test_user_journey.py`: Complete user workflow tests

## Writing New E2E Tests

1. Use the `page` fixture for browser interactions
2. Use the `api_client` fixture for direct API calls
3. Use the `test_user` fixture for authenticated user scenarios
4. Mark tests with `@pytest.mark.e2e`

Example:
```python
@pytest.mark.e2e
async def test_my_feature(page: Page, api_client):
    page.goto("http://localhost:3000")
    # Your test code here
```

