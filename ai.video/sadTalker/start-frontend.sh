#!/bin/bash

echo "========================================"
echo "   SadTalker Frontend Dev Server"
echo "========================================"
echo

if [ ! -d "web/node_modules" ]; then
    echo "[INFO] Installing dependencies..."
    cd web && npm install && cd ..
fi

echo "Starting frontend dev server on http://localhost:3802"
echo "Press Ctrl+C to stop"
echo

cd web
npm run dev
