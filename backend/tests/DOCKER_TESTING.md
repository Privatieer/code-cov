# Docker-Based Testing (No Local Poetry Needed!)

## Why Docker?

✅ **No local Python/Poetry installation needed**  
✅ **Consistent environment** (matches CI/CD exactly)  
✅ **All dependencies pre-installed**  
✅ **Works on any machine** (macOS, Linux, Windows)  
✅ **No Python version conflicts**

## Quick Start

### Run All Tests

```bash
# From project root
./run_tests.sh

# Or directly with Docker
docker compose exec backend pytest tests/unit tests/integration -v
```

### Run Specific Test Types

```bash
# Unit tests only
./run_tests.sh unit

# Integration tests only  
./run_tests.sh integration

# All tests (unit + integration)
./run_tests.sh all

# E2E tests (requires frontend running)
./run_tests.sh e2e
```

## Prerequisites

Only Docker and Docker Compose are needed:

```bash
# Check Docker is installed
docker --version
docker compose version
```

## What Gets Tested

- ✅ **Unit Tests** (`tests/unit/`) - Fast, isolated tests with mocks
- ✅ **Integration Tests** (`tests/integration/`) - API tests with real database
- ⚠️ **E2E Tests** (`tests/e2e/`) - Browser automation (requires frontend)

## Test Results

All **54 tests** pass:
- Unit tests: Fast feedback (< 5 seconds)
- Integration tests: API validation (< 30 seconds)

## Troubleshooting

### "Error: No such container: backend"

Make sure Docker containers are running:
```bash
docker compose up -d db redis backend
```

### "Connection refused" errors

Ensure database is ready:
```bash
docker compose ps  # Check all services are "Up"
```

### Want to see test output in real-time?

```bash
docker compose exec backend pytest tests/unit tests/integration -v -s
```

## CI/CD Integration

GitHub Actions uses the same Docker-based approach:
- ✅ Same test commands
- ✅ Same environment
- ✅ Same results

## Summary

**You don't need Poetry locally!** Just use Docker:

```bash
./run_tests.sh  # That's it! 🎉
```

All tests run in isolated containers with zero local setup.

