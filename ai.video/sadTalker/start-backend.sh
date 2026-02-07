#!/bin/bash

echo "========================================"
echo "   SadTalker Backend Server"
echo "========================================"
echo

if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run setup.sh first."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting backend server on http://localhost:8802"
echo "Press Ctrl+C to stop"
echo

cd backend
python api.py
