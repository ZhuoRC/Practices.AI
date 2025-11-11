#!/usr/bin/env python3
"""
AI Audio TTS Backend Startup Script
Ensures the backend runs in the virtual environment
"""

import os
import sys
import subprocess
from pathlib import Path

def check_and_activate_venv():
    """Check if we're running in the virtual environment, and if not, restart with it."""

    # Get the project root directory
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"

    # Determine the virtual environment activation script path
    if os.name == 'nt':  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_activate = venv_path / "Scripts" / "activate.bat"
    else:  # Linux/Mac
        venv_python = venv_path / "bin" / "python"
        venv_activate = venv_path / "bin" / "activate"

    # Check if we're already running in the virtual environment
    if sys.prefix != sys.base_prefix:
        print("✓ Running in virtual environment")
        return True

    # Check if virtual environment exists
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print(f"Expected location: {venv_path}")
        print("Please create a virtual environment first:")
        print("  python -m venv venv")
        return False

    if not venv_python.exists():
        print("❌ Virtual environment Python not found!")
        print(f"Expected location: {venv_python}")
        print("Please ensure the virtual environment is properly created.")
        return False

    print("🔄 Restarting with virtual environment...")

    # Restart the script with the virtual environment Python
    try:
        # Get the arguments needed to run the main application
        main_script = project_root / "main.py"
        subprocess.run([str(venv_python), str(main_script)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
        return True

def main():
    """Main startup function."""
    print("🚀 AI Audio TTS Backend Startup")
    print("=" * 50)

    if not check_and_activate_venv():
        sys.exit(1)

if __name__ == "__main__":
    main()