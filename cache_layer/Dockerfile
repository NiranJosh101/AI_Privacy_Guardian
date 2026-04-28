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


# --- Stage 2: Final ---
FROM python:3.11-slim
WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Ensure imports work
ENV PYTHONPATH=/app/app

EXPOSE 8007


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]