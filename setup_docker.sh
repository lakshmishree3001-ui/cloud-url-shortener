#!/bin/bash
# ==============================================================================
# AWS EC2 Docker Setup & Runner Script
# Installs Docker, builds the image, and launches the containerized URL Shortener
# ==============================================================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "🐳 Setting up Docker Containerization on AWS EC2"
echo "Working directory: $SCRIPT_DIR"
echo "=========================================================="

# 1. Install Docker and Docker Compose if not present
if ! command -v docker &> /dev/null; then
    echo "1. Installing Docker engine..."
    sudo apt-get update -y
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "   -> Docker installed and service started."
else
    echo "1. Docker is already installed."
fi

# 2. Stop any existing container with the same name
echo "2. Cleaning up any old container..."
sudo docker stop url-shortener-app 2>/dev/null || true
sudo docker rm url-shortener-app 2>/dev/null || true

# 3. Build Docker container image
echo "3. Building Docker image: cloud-url-shortener:latest..."
sudo docker build -t cloud-url-shortener:latest .

# 4. Run the containerized service
echo "4. Running container with volume persistence on port 8000..."
sudo docker run -d \
    -p 8000:8000 \
    -v url-shortener-data:/app/data \
    --name url-shortener-app \
    --restart unless-stopped \
    cloud-url-shortener:latest

# 5. Wait for container to initialize and probe health
echo "5. Waiting for container to start (5 seconds)..."
sleep 5

echo "6. Probing container health status..."
sudo docker ps --filter "name=url-shortener-app"

echo ""
echo "7. Testing HTTP /health endpoint inside container:"
curl -s http://localhost:8000/health | grep "healthy" && echo "   -> Health check PASSED!" || echo "   -> Health check pending"

echo "=========================================================="
echo "🚀 Docker containerization is complete and running!"
echo ""
echo "Useful container commands:"
echo "  sudo docker ps                          # Check running container"
echo "  sudo docker logs -f url-shortener-app   # View live container logs"
echo "  sudo docker stop url-shortener-app      # Stop container"
echo "  sudo docker restart url-shortener-app   # Restart container"
echo "=========================================================="
