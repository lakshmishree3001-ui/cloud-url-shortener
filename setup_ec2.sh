#!/bin/bash
# ==============================================================================
# AWS EC2 Cloud Setup Script for Cloud-Based URL Shortener
# Automates installation of Python 3, venv, Docker, and project dependencies
# ==============================================================================

set -e

echo "=========================================================="
echo "🚀 Setting up AWS EC2 Cloud Environment for URL Shortener"
echo "=========================================================="

# 1. Update OS packages
echo "1. Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. Install Python 3, pip, venv, and unzip
echo "2. Installing Python 3, pip, and developer tools..."
sudo apt-get install -y python3 python3-pip python3-venv unzip git curl

# 3. Install Docker
echo "3. Installing Docker Engine for Lab 13..."
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER || true

# 4. Set up Python Virtual Environment
echo "4. Setting up Python virtual environment..."
cd ~/cloud-url-shortener || cd $(pwd)
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
echo "5. Installing project dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Run verification tests
echo "6. Running automated test verification..."
pytest -v

echo "=========================================================="
echo "✅ AWS EC2 Cloud Environment is 100% Ready!"
echo "To start your cloud server on port 8000:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "=========================================================="
