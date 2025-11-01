# GPU Setup Guide for RAG System

## Current Status
- ✅ **GPU Detected**: NVIDIA GeForce RTX 3050
- ✅ **CUDA Version**: 13.0
- ❌ **PyTorch**: CPU version (2.9.0+cpu) - needs upgrade

## Why GPU Matters
- **CPU Embedding Speed**: ~100-200 chunks/minute
- **GPU Embedding Speed**: ~2000-5000 chunks/minute
- **Performance Boost**: **10-50x faster** 🚀

## Installation Steps

### Option 1: Install PyTorch with CUDA Support (Recommended)

Since you have CUDA 13.0, you should install PyTorch with CUDA 12.x support (PyTorch doesn't have CUDA 13 builds yet, but CUDA 12.x is backward compatible).

```bash
# Activate virtual environment
cd backend
.\venv\Scripts\activate

# Uninstall CPU version
pip uninstall torch torchvision torchaudio -y

# Install GPU version with CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Option 2: Using CUDA 11.8 (Alternative)

If you encounter issues with CUDA 12.x:

```bash
# Install GPU version with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Verify Installation

After installation, verify GPU is detected:

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3050 Laptop GPU
```

## Restart Backend

After installing GPU PyTorch:

```bash
# Stop the current backend (Ctrl+C)
# Restart
python run.py
```

You should now see:
```
Using device: cuda
Batch size: 32
```

## Troubleshooting

### Issue: CUDA out of memory

If you get CUDA out of memory errors, reduce batch size in `.env`:

```bash
# For RTX 3050 with 6GB VRAM, use smaller batch size
EMBEDDING_BATCH_SIZE_GPU=16  # or even 8
```

### Issue: Still using CPU after installation

1. Check if torch sees CUDA:
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. If False, check NVIDIA driver:
   ```bash
   nvidia-smi
   ```

3. If driver is not working, update NVIDIA drivers from:
   https://www.nvidia.com/Download/index.aspx

### Issue: Multiple CUDA versions

If you have multiple CUDA versions installed, PyTorch will use the one it was compiled with. This is fine as long as your driver supports it (your driver supports CUDA 13.0, so it supports older versions too).

## Performance Comparison

### Before (CPU):
- Upload 100-page PDF: **2-5 minutes**
- Query: 1-2 seconds

### After (GPU):
- Upload 100-page PDF: **10-30 seconds** ⚡
- Query: 0.5-1 second

## Additional Tips

1. **Monitor GPU Usage**:
   ```bash
   nvidia-smi -l 1  # Update every 1 second
   ```

2. **Optimize Batch Size**:
   - RTX 3050 (6GB): 16-32
   - RTX 3060 (12GB): 32-64
   - RTX 3080 (10GB): 32-64

3. **Mixed Precision** (Future optimization):
   - Can reduce memory usage by 50%
   - Currently not implemented

## Summary

Run these commands to enable GPU:

```bash
cd backend
.\venv\Scripts\activate
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
python run.py
```

Then check the startup log for `Using device: cuda` 🎉
