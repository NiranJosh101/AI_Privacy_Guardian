# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Set environment variables to keep Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# [CRITICAL FOR CACHING] 
# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies into a local folder
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Final Slim Image ---
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed site-packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the rest of the application code
# Since this is the last step, code changes won't trigger a re-install of packages
COPY . .

# Create a non-privileged user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the Gateway's public port
EXPOSE 8000

# Start the Gateway
# We use host 0.0.0.0 so it's reachable outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]