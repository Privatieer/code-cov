FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/backend/

# Install dependencies (including dev dependencies for testing)
WORKDIR /app/backend
RUN poetry install --no-interaction --no-ansi --no-root && \
    pip install pytest-cov || true  # Ensure pytest-cov is available even if Poetry install misses it

# Copy the rest of the application
COPY . /app/backend

# Set python path so "backend.src..." imports work
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8004
