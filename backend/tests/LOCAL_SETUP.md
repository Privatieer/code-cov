# Local Test Setup Guide

## Quick Start: Use Docker (Recommended)

The easiest way to run tests is using Docker, which ensures a consistent environment:

```bash
# Start services
docker compose up -d db redis

# Run tests
docker compose exec backend pytest tests/unit tests/integration -v
```

## Local Setup with Poetry

If you want to run tests locally without Docker, you need Python 3.11 or 3.12 (not 3.13).

### Why Python 3.13 Doesn't Work

Python 3.13 introduced breaking changes that `asyncpg` 0.29.0 hasn't adapted to yet. You'll see compilation errors like:
```
error: call to undeclared function '_PyInterpreterState_GetConfig'
```

### Setup Steps

1. **Install Python 3.11 or 3.12** (if not already installed):
   ```bash
   # macOS with Homebrew
   brew install python@3.11
   # or
   brew install python@3.12
   ```

2. **Configure Poetry to use the correct Python version**:
   ```bash
   cd backend
   poetry env use python3.11
   # or
   poetry env use python3.12
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Run tests**:
   ```bash
   poetry run pytest tests/unit tests/integration -v
   ```

### Verify Python Version

```bash
poetry run python --version
# Should show: Python 3.11.x or Python 3.12.x (NOT 3.13)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'asyncpg'"

This means dependencies aren't installed. Run:
```bash
cd backend
poetry install
```

### "asyncpg compilation errors"

This means you're using Python 3.13. Switch to Python 3.11 or 3.12:
```bash
cd backend
poetry env use python3.11
poetry install
```

### "ModuleNotFoundError: No module named 'backend'"

This means PYTHONPATH isn't set correctly. The `pytest.ini` should handle this automatically, but if not:
```bash
# From backend directory
export PYTHONPATH=..
poetry run pytest tests/unit -v
```

Or use the helper script which handles this automatically:
```bash
cd backend
./scripts/run_tests.sh all
```

## Recommendation

**Use Docker for testing** - it's simpler, faster to set up, and matches the CI/CD environment exactly. Only use local Poetry setup if you need to debug or develop tests themselves.

