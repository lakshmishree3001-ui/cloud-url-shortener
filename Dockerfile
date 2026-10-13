# ==============================================================================
# Production Dockerfile for Cloud-Based URL Shortener
# Maps to AWS ECS Fargate / AWS App Runner Container Deployments
# ==============================================================================
FROM python:3.12-slim

# Set environment variables for optimized Python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DATABASE_URL="sqlite:////app/data/urls.db"

# Install curl for container health check probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and persistent data directory (AWS Security Best Practice)
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 -m appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appgroup /app

WORKDIR /app

# Copy dependency definition first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and test suite
COPY app/ ./app
COPY tests/ ./tests

# Ensure non-root ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose FastAPI listening port
EXPOSE 8000

# Container healthcheck probe matching AWS Application Load Balancer (ALB) healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch production uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
