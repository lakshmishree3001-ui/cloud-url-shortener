#!/bin/bash
# ==============================================================================
# AWS EC2 Cloud Setup Script for Cloud-Based URL Shortener
# Supports Python 3.12, 3.13, and 3.14 on Ubuntu with PyO3 Forward Compatibility
# ==============================================================================

set -e

# Always run inside the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "🚀 Setting up AWS EC2 Cloud Environment for URL Shortener"
echo "Working directory: $SCRIPT_DIR"
echo "=========================================================="

# 1. Export PyO3 ABI3 forward compatibility for Python 3.14
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# 2. Enable 2GB Swap memory (prevents t2.micro Out-Of-Memory errors)
if [ ! -f /swapfile ]; then
    echo "1. Adding 2GB swap memory..."
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab || true
    echo "   -> Swap configured successfully."
else
    echo "1. Swap already enabled."
fi

# 3. Install system prerequisites & build tools
echo "2. Installing system tools..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip unzip git curl build-essential

# 4. Clean and recreate virtual environment
echo "3. Creating clean Python virtual environment..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 5. Upgrade pip and build tools
echo "4. Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# 6. Install pydantic with Python 3.14 ABI3 forward compatibility
echo "5. Installing pydantic and core dependencies..."
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install --upgrade pydantic pydantic-core

# 7. Install remaining project dependencies
echo "6. Installing remaining project requirements..."
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt

# 8. Run test verification
echo "7. Running test verification..."
pytest -v

echo "=========================================================="
echo "✅ AWS EC2 Cloud Environment is 100% Ready!"
echo ""
echo "To start your live cloud server:"
echo "  cd $SCRIPT_DIR"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "=========================================================="
