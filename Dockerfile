FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/incoming data/transcripts data/briefings data/analysis

# Expose port 8000 (FastAPI automation server)
EXPOSE 8000

# Health check hits the server's /health endpoint
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Run the Phase 2 automation server.
# Railway sets $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn brain.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
