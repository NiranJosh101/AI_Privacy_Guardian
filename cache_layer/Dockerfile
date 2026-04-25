# --- Stage 1: Builder (The Kitchen) ---
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal build tools for redis-py and pydantic extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# [CACHING] Copy only requirements to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies to a temporary install directory
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Final (The Runner) ---
FROM python:3.11-slim

WORKDIR /app

# Copy the pre-compiled/installed libraries from the builder
COPY --from=builder /install /usr/local

# Copy the application source code
# This includes your main.py, configs/, and utils/
COPY . .

# Create a non-privileged user for security (Principle of Least Privilege)
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the internal port for the Cache Service API
EXPOSE 8000

# Start the service
# Using python main.py as requested for your internal services
CMD ["python", "main.py"]