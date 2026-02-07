#!/bin/bash

echo "========================================"
echo "   SadTalker Video Generator"
echo "========================================"
echo

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run setup.sh first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "web/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    cd web && npm install && cd ..
fi

echo "Starting services..."
echo "  Backend API: http://localhost:8802"
echo "  Frontend:    http://localhost:3802"
echo

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend server..."
source venv/bin/activate
cd backend && python api.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend dev server..."
cd web && npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "========================================"
echo "Services started!"
echo
echo "  Backend API: http://localhost:8802"
echo "  Frontend:    http://localhost:3802"
echo
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Wait for processes
wait
