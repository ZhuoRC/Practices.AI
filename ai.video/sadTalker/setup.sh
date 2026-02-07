#!/bin/bash

echo "========================================"
echo "SadTalker Video Generator Setup"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Create virtual environment
echo "[1/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "[3/5] Upgrading pip..."
pip install --upgrade pip

# Install PyTorch
echo "[4/5] Installing PyTorch..."
echo "(Detecting CUDA availability...)"

if command -v nvidia-smi &> /dev/null; then
    echo "CUDA detected, installing PyTorch with CUDA 11.8 support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "No CUDA detected, installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio
fi

# Install other dependencies
echo "[5/5] Installing other dependencies..."
pip install -r requirements.txt

echo
echo "========================================"
echo "Setup completed!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Download SadTalker checkpoints:"
echo "   - Visit https://github.com/OpenTalker/SadTalker#2-download-models"
echo "   - Place checkpoints in SadTalker/checkpoints folder"
echo
echo "2. Run the server:"
echo "   ./run.sh"
echo
