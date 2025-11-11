#!/usr/bin/env python3
"""
Setup Local TTS Service (Piper TTS)
Downloads and configures free offline TTS service
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path

def download_file(url, filename, description):
    """Download a file with progress indication."""
    print(f"Downloading {description}...")
    print(f"URL: {url}")
    print(f"Saving to: {filename}")

    def reporthook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            print(f"\rProgress: {percent}% ({block_num * block_size}/{total_size} bytes)", end="")
        else:
            print(f"\rDownloaded: {block_num * block_size} bytes", end="")

    try:
        urllib.request.urlretrieve(url, filename, reporthook)
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nDownload failed: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract a zip file."""
    print(f"Extracting {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction complete!")
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def extract_tar(tar_path, extract_to):
    """Extract a tar.gz file."""
    print(f"Extracting {tar_path}...")
    try:
        with tarfile.open(tar_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)
        print("Extraction complete!")
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def main():
    """Setup local TTS service."""
    print("Setting up Free Local TTS Service (Piper TTS)")
    print("=" * 60)
    print()

    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    os.chdir(models_dir)

    print("This will download and install:")
    print("- Piper TTS engine (~200MB)")
    print("- English voice model (~50MB)")
    print()
    print("Total download size: ~250MB")
    print()

    response = input("Continue with installation? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Installation cancelled.")
        return

    # Download Piper TTS
    piper_url = "https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip"
    piper_zip = "piper_windows_amd64.zip"

    if not download_file(piper_url, piper_zip, "Piper TTS Engine"):
        return False

    if not extract_zip(piper_zip, "."):
        return False

    # Download voice model
    voice_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.tar.gz"
    voice_tar = "en_US-lessac-medium.tar.gz"

    if not download_file(voice_url, voice_tar, "English Voice Model (Lessac Medium)"):
        return False

    if not extract_tar(voice_tar, "."):
        return False

    # Rename files to match expected naming
    renames = [
        ("en_US-lessac-medium.onnx", "en-us-lessac-medium.onnx"),
        ("en_US-lessac-medium.onnx.json", "en-us-lessac-medium.onnx.json")
    ]

    for old_name, new_name in renames:
        if os.path.exists(old_name) and not os.path.exists(new_name):
            os.rename(old_name, new_name)
            print(f"Renamed: {old_name} -> {new_name}")

    # Cleanup
    cleanup_files = [piper_zip, voice_tar]
    for file in cleanup_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned up: {file}")

    print()
    print("🎉 Installation Complete!")
    print()
    print("📁 Files installed:")
    print("  - Piper TTS: piper.exe")
    print("  - Voice model: en-us-lessac-medium.onnx")
    print("  - Model config: en-us-lessac-medium.onnx.json")
    print()
    print("🎯 Usage:")
    print("  1. Restart the backend server")
    print("  2. Select 'local' provider in the frontend")
    print("  3. Choose 'en-us-lessac-medium' voice")
    print()
    print("✨ This is completely free and works offline!")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)