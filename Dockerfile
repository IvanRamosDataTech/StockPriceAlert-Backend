# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies required by numpy/pandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (separate layer — cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ ./backend/

# Environment variables are injected at runtime via docker-compose env_file.
# Do NOT bake secrets into the image.

# Single worker is mandatory: APScheduler runs in-process.
# More than 1 worker would spawn duplicate schedulers → duplicate alerts.
CMD ["gunicorn", "backend:create_app()", "--workers=1", "--threads=4", "--bind=0.0.0.0:8000"]
