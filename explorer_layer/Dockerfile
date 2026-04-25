# Use the official Playwright Python image as the ONLY stage
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# 1. Install dependencies
# We do this first so it stays cached if your code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. [FIX] Verify/Install Chromium
# In this specific Microsoft image, Chromium is usually at /ms-playwright
# We run this just to ensure Crawl4AI has everything it needs.
# Using 'python -m' is the safest way to call it.
RUN python -m playwright install chromium

# 3. Copy your service code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV CRAWL4AI_JSON_LOGGING=true

# Expose ports
EXPOSE 8000 8001

CMD ["python", "main.py"]