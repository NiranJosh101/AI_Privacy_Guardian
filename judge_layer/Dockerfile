# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Build tools for NLP/Validation libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# [CACHING] Dependencies first
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Final Slim Image ---
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /install /usr/local

# Copy Judge logic (evaluators, scoring rubrics, etc.)
COPY . .

# Run as non-privileged user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Start the Judge
CMD ["python", "main.py"]