# Use the official Playwright Python image as the ONLY stage
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# 1. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. [FIX] Verify/Install Chromium
RUN python -m playwright install chromium

# 3. Copy your service code
COPY . .

# 4. [NEW] Prepare the entrypoint script
# Ensure it has Linux-style line endings and is executable
RUN chmod +x entrypoint.sh

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV CRAWL4AI_JSON_LOGGING=true

# Expose ports 
# 8000 for the Explorer API, 8001 for the internal MCP server
EXPOSE 8000 8001

# 5. [MODIFIED] Use the entrypoint script instead of a direct python call
CMD ["./entrypoint.sh"]