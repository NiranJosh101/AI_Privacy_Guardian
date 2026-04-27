# --- Stage 1: Builder (The Kitchen) ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Final (The Runner) ---
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# Copy everything (including the cache_layer folder)
COPY . .

# 1. Update permissions for the whole app
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 2. CHANGE WORKING DIRECTORY to where main.py actually is
WORKDIR /app/cache_layer

EXPOSE 8000

# Now 'main.py' is in the current directory
CMD ["python", "main.py"]