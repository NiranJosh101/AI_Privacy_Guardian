# --- Stage 1: Build ---
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy AS builder

WORKDIR /app

# 1. Cache the pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Final (The "Explorer" Image) ---
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# 2. Bring over the Python libraries
COPY --from=builder /install /usr/local

# 3. [CRITICAL] Install the Chromium binary for Crawl4AI
# This layer stays cached unless you change this line
RUN playwright install chromium && playwright install-deps chromium

# 4. Copy your code (Main service + MCP server)
COPY . .

# Environment variables for Crawl4AI performance
ENV PYTHONUNBUFFERED=1
ENV CRAWL4AI_JSON_LOGGING=true

# Expose ports for both the Main API and the MCP SSE server
EXPOSE 8000 8001