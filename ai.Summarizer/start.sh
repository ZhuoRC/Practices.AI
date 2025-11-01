#!/bin/bash

echo "============================================"
echo "  AI Summarizer - Starting Services"
echo "============================================"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "[ERROR] backend/.env file not found!"
    echo "Please copy backend/.env.example to backend/.env and configure it."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "[1/4] Checking Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "[2/4] Installing/Updating Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "[3/4] Checking Node.js dependencies..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "[4/4] Starting services..."
echo ""
echo "============================================"
echo "  Backend: http://localhost:8002"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8002/docs"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start backend
cd ../backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait
