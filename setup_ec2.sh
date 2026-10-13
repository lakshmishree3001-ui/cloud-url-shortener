#!/bin/bash
# ==============================================================================
# AWS EC2 Cloud Setup Script for Cloud-Based URL Shortener (Updated & Resilient)
# Automatically enables 2GB Swap (prevents t2.micro OOM SIGKILL) and uses Python 3.12
# ==============================================================================

set -e

echo "=========================================================="
echo "🚀 Setting up AWS EC2 Cloud Environment for URL Shortener"
echo "=========================================================="

# 1. Enable 2GB Swap to prevent t2.micro Out-Of-Memory (OOM SIGKILL)
if [ ! -f /swapfile ]; then
    echo "1. Adding 2GB swap memory (prevents t2.micro OOM errors)..."
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab || true
    echo "   -> Swap enabled successfully."
else
    echo "1. Swap already configured."
fi

# 2. Update packages and install python3.12 and build essentials
echo "2. Installing Python 3.12, venv, and developer dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip unzip git curl build-essential || sudo apt-get install -y python3 python3-venv python3-pip

# 3. Determine best Python command (prefer python3.12 for pre-built wheels)
if command -v python3.12 &> /dev/null; then
    PY_BIN="python3.12"
else
    PY_BIN="python3"
fi
echo "   -> Using Python binary: $PY_BIN"

# 4. Rebuild virtual environment cleanly
echo "3. Creating isolated virtual environment..."
rm -rf venv
$PY_BIN -m venv venv
source venv/bin/activate

# 5. Upgrade pip, wheel, and setuptools
echo "4. Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# 6. Install project dependencies
echo "5. Installing project dependencies from requirements.txt..."
pip install -r requirements.txt

# 7. Run automated test suite
echo "6. Running test suite..."
pytest -v

echo "=========================================================="
echo "✅ AWS EC2 Cloud Environment is 100% Ready!"
echo ""
echo "To start your live cloud server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "=========================================================="
