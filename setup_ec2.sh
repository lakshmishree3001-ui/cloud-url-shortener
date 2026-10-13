#!/bin/bash
# ==============================================================================
# AWS EC2 Cloud Setup Script for Cloud-Based URL Shortener
# Uses uv to guarantee pristine Python 3.12 with pre-compiled binary wheels
# ==============================================================================

set -e

# Always run inside the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "🚀 Setting up AWS EC2 Cloud Environment (Python 3.12 + uv)"
echo "Working directory: $SCRIPT_DIR"
echo "=========================================================="

# 1. Enable 2GB Swap memory (prevents t2.micro memory pressure)
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

# 2. Install curl and build tools if missing
sudo apt-get update -y
sudo apt-get install -y curl unzip git

# 3. Install Astral uv (industry standard fast Python toolchain)
if ! command -v uv &> /dev/null; then
    echo "2. Installing Astral uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

# 4. Create pristine Python 3.12 virtual environment (downloads standalone binary)
echo "3. Creating Python 3.12 virtual environment..."
rm -rf venv
uv venv --python 3.12 venv
source venv/bin/activate

# 5. Install all project dependencies using uv (ultra-fast pre-built wheels)
echo "4. Installing dependencies with pre-built binary wheels..."
uv pip install -r requirements.txt

# 6. Run test verification
echo "5. Running automated tests..."
pytest -v

echo "=========================================================="
echo "✅ AWS EC2 Cloud Environment is 100% Ready!"
echo ""
echo "To start your live cloud server:"
echo "  cd $SCRIPT_DIR"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "=========================================================="
