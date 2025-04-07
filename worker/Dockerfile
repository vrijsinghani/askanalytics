# Build stage for dependencies
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Final stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/root/.local/bin:$PATH"

# Add build arguments for version and commit
ARG VERSION=latest
ARG COMMIT=unknown
ARG COMMIT_DATE
ENV VERSION=$VERSION
ENV COMMIT=$COMMIT
ENV COMMIT_DATE=$COMMIT_DATE
ENV IS_DOCKER=true

# Install runtime dependencies and UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Create directory for env files
RUN mkdir -p /app/env-files

WORKDIR /app

# Copy requirements file
COPY requirements.docker.txt ./

# Create venv and install dependencies
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install -r requirements.docker.txt

# Copy example env file
COPY env-files/.env.example /app/env-files/

# Copy only necessary application files
COPY apps ./apps
COPY core ./core
RUN mkdir -p /app/logs /app/media

# Create non-root user
RUN useradd -m -u 1000 celery && \
    chown -R celery:celery /app

# Ensure we use the venv python
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER celery

# Default command runs both worker and beat
# Override with specific command if needed
CMD ["celery", "-A", "apps.tasks", "worker", "-l", "info"]
