#!/bin/bash

echo "🚀 AI Audio TTS Backend Startup"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create a virtual environment first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "✅ Installing dependencies (if needed)..."
pip install -r requirements.txt

echo "✅ Starting backend on port 7000..."
echo "📍 Backend will be available at: http://localhost:7000"
echo "📍 API Documentation: http://localhost:7000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py