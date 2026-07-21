# DreamCobots — Production Dockerfile
# Multi-stage build for minimal image size

# ── Stage 1: Build / dependency install ──────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as non-root
RUN addgroup --gid 1001 dreamco && \
    adduser --uid 1001 --gid 1001 --no-create-home --disabled-password dreamco

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=dreamco:dreamco . .

# Drop to non-root user
USER dreamco

# Expose port for any web-facing services (Flask/FastAPI)
EXPOSE 8000

# Default command — override in docker-compose or k8s manifests
CMD ["python", "-m", "pytest", "tests/", "--ignore=tests/test_backend.py", "-q"]
