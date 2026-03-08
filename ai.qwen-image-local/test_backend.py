#!/usr/bin/env python3
"""
Simple test script to verify backend API can start
"""
import sys
import subprocess

print("Testing backend API startup...")
print("=" * 50)

try:
    # Try to start the backend API
    result = subprocess.run(
        [sys.executable, "-c", "import uvicorn; import sys; sys.path.insert(0, '.'); from qwen_image_edit.qwen_image_edit_api import app; print('App imported successfully')"],
        cwd=".",
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n✓ Backend API can be imported successfully")
    else:
        print(f"\n✗ Backend API import failed with return code {result.returncode}")
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    print("\n✗ Backend API import timed out (30s)")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("Test complete")