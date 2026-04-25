# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build-essential if your NLP libraries (like pydantic or tiktoken) 
# need to compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# [CACHING] Copy requirements first
COPY requirements.txt .

# Install dependencies into a separate directory
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Final Slim Image ---
FROM python:3.12-slim

WORKDIR /app

# Copy the pre-installed libraries from the builder
COPY --from=builder /install /usr/local

# Copy the Interpreter logic (chains, prompts, and schemas)
COPY . .

# Security: Run as non-privileged user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the internal port (The Interpreter is private, not public)
EXPOSE 8000

# Start the Interpreter
CMD ["python", "main.py"]