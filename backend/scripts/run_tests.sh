#!/bin/bash
# Test runner script for easy test execution
# Usage: ./scripts/run_tests.sh [unit|integration|all|e2e]
#
# This script sets PYTHONPATH correctly so imports work from the backend directory

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the backend directory (parent of scripts)
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
# Get the project root (parent of backend)
PROJECT_ROOT="$( cd "$BACKEND_DIR/.." && pwd )"

# Set PYTHONPATH to project root so 'backend' module can be found
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Change to backend directory
cd "$BACKEND_DIR"

TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
  unit)
    echo "🧪 Running unit tests..."
    poetry run pytest tests/unit -v -m unit
    ;;
  integration)
    echo "🧪 Running integration tests..."
    poetry run pytest tests/integration -v -m integration
    ;;
  all)
    echo "🧪 Running all tests (unit + integration)..."
    poetry run pytest tests/unit tests/integration -v
    ;;
  e2e)
    echo "🧪 Running E2E tests..."
    echo "⚠️  Note: E2E tests require frontend and backend services to be running"
    echo "⚠️  Make sure you've started: docker compose up backend db redis"
    echo "⚠️  And frontend: cd frontend && npm run dev"
    poetry run pytest tests/e2e -v -m e2e -o "ignore="
    ;;
  *)
    echo "Usage: $0 [unit|integration|all|e2e]"
    echo ""
    echo "  unit        - Run only unit tests"
    echo "  integration - Run only integration tests"
    echo "  all         - Run unit + integration tests (default)"
    echo "  e2e         - Run E2E tests (requires running services)"
    exit 1
    ;;
esac

