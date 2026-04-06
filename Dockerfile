# ==========================================================================
# Spooder — Emotive Spider Bot for Fluxer
# The Alphabet Cartel
# ==========================================================================
# Multi-stage Docker build — Python 3.12 + tini + PUID/PGID
# FILE VERSION: v1.0.0
# LAST MODIFIED: 2026-04-05
# ==========================================================================

# ── Stage 1: Builder ──────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ARG DEFAULT_UID=1000
ARG DEFAULT_GID=1000

# Install tini for PID 1 signal handling
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -g ${DEFAULT_GID} appgroup && \
    useradd -m -u ${DEFAULT_UID} -g ${DEFAULT_GID} appuser

# Copy venv from builder
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
COPY --from=builder /opt/venv /opt/venv

# Copy application
WORKDIR /app
COPY docker-entrypoint.py /app/docker-entrypoint.py
COPY src/ /app/src/

# Create writable directories
RUN mkdir -p /app/logs

# NOTE: Do NOT use USER directive — entrypoint handles privilege dropping
ENTRYPOINT ["/usr/bin/tini", "--", "python", "/app/docker-entrypoint.py"]
CMD ["python", "src/main.py"]
