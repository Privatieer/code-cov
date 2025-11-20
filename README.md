# Task Tracker (Mars-Grade Edition)

A clean architecture, full-stack Task Tracker application built with Python (FastAPI), React (Material UI), and modern DevOps practices.

## Features
- **Clean Architecture**: Domain-centric design with loose coupling.
- **Secure Auth**: JWT-based authentication with password hashing.
- **Task Management**: CRUD operations with PostgreSQL.
- **File Attachments**: S3-compatible storage (MinIO) for file uploads.
- **Background Workers**: Celery + Redis for due date notifications.
- **Observability**: Structured JSON logging and Prometheus metrics.

## Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy (Async), Pydantic
- **Frontend**: React, TypeScript, Vite, Material UI, TanStack Query
- **Infrastructure**: Docker Compose, Postgres 16, Redis 7, MinIO

## How to Run

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev, optional)

### Quick Start

1. **Start Infrastructure & Backend**
   ```bash
   docker-compose up -d --build
   ```
   This starts:
   - Postgres (DB)
   - Redis (Broker)
   - MinIO (Object Storage)
   - Worker (Celery)
   - Backend API (FastAPI)

2. **Run Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the UI at `http://localhost:3000`.

3. **Access API Docs**
   - Swagger UI: `http://localhost:8004/docs`
   - Metrics: `http://localhost:8004/metrics`

## Running Tests

**No local Poetry installation needed!** All tests run in Docker with code coverage.

```bash
# Run all tests with coverage (default)
./run_tests.sh

# Or run specific test types
./run_tests.sh unit          # Unit tests only
./run_tests.sh integration   # Integration tests only
./run_tests.sh all           # All tests (default)
./run_tests.sh e2e           # E2E tests (requires frontend running)
./run_tests.sh all --no-cov  # Skip coverage report
```

**Coverage Reports:**
- **Terminal**: Summary with missing lines
- **HTML**: `backend/htmlcov/index.html` (open in browser)
- **XML**: `backend/coverage.xml` (for CI/CD)

**Or use Docker directly:**
```bash
docker compose exec backend poetry run pytest tests/unit tests/integration -v --cov=backend.src --cov-report=html --cov-report=term
```

All 54 tests (unit + integration) pass! ✅ Coverage reports generated automatically.

## Project Structure

```
/
├── backend/              # FastAPI Application
│   ├── src/
│   │   ├── domain/       # Business Logic (Entities, Interfaces)
│   │   ├── application/  # Use Cases
│   │   ├── infrastructure/# DB, Auth, Adapters
│   │   └── interface/    # API Routers
├── frontend/             # React Application
└── docker-compose.yml    # Infrastructure Definition
```

