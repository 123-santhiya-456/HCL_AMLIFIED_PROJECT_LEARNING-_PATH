# Use a slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Initialize database with seed data
RUN python database/seed.py

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN printf '#!/bin/bash\nuvicorn backend.main:app --host 0.0.0.0 --port 8000 &\nstreamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0\n' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
