# Memory Optimization Guide for Qwen-Image API

## The Problem

The Qwen-Image model is a 20B parameter model that requires significant GPU memory (VRAM). If you're getting "CUDA out of memory" errors, you need to use one of the optimized versions.

## Which Version Should I Use?

### 1. **qwen_image_api.py** - Standard Version
**For: GPUs with 16GB+ VRAM**

```bash
python qwen_image_api.py
```

**Pros:**
- Fastest generation speed
- Highest quality
- Supports full resolution (up to 2048x2048)

**Cons:**
- Requires 16GB+ VRAM
- Will OOM on smaller GPUs

---

### 2. **qwen_image_api_optimized.py** - Optimized Version
**For: GPUs with 10-16GB VRAM**

```bash
python qwen_image_api_optimized.py
```

**Optimizations:**
- Attention slicing (slice_size=1)
- VAE slicing and tiling
- Float16 precision
- Model CPU offload for <12GB GPUs

**Pros:**
- Good balance of speed and memory
- Works on mid-range GPUs
- Still supports high resolution

**Cons:**
- Slightly slower than standard
- May still OOM on <10GB GPUs

---

### 3. **qwen_image_api_low_vram.py** - Low VRAM Version
**For: GPUs with 6-10GB VRAM** ⭐ **RECOMMENDED FOR YOUR CASE**

```bash
python qwen_image_api_low_vram.py
```

**Optimizations:**
- Sequential CPU offload (most aggressive)
- Aggressive attention slicing (slice_size=1)
- VAE slicing (tiling disabled for compatibility)
- BFloat16 precision (better numerical stability)
- Automatic memory cleanup
- Lower default resolution (768x768)

**Pros:**
- Works on 6-8GB GPUs
- Detailed logging and error messages
- Automatic memory management

**Cons:**
- Slower generation (components move between CPU/GPU)
- Recommended max resolution: 1024x1024

---

## Quick Decision Chart

```
Your GPU VRAM:
├─ 16GB+     → Use qwen_image_api.py
├─ 10-16GB   → Use qwen_image_api_optimized.py
├─ 6-10GB    → Use qwen_image_api_low_vram.py
└─ <6GB      → Use CPU mode (see below)
```

## Check Your GPU Memory

Run this command to see your GPU specs:

```bash
python check_gpu.py
```

Or use this quick Python command:

```python
import torch
if torch.cuda.is_available():
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Total VRAM: {gpu_mem:.1f} GB")
else:
    print("No GPU available")
```

## Recommended Settings by GPU Size

### 16GB+ VRAM
```python
{
    "width": 1280,
    "height": 1280,
    "num_inference_steps": 50
}
```

### 12-16GB VRAM
```python
{
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 40
}
```

### 8-12GB VRAM
```python
{
    "width": 768,
    "height": 768,
    "num_inference_steps": 30
}
```

### 6-8GB VRAM
```python
{
    "width": 512,
    "height": 512,
    "num_inference_steps": 20
}
```

## CPU Mode (No GPU)

If you don't have a GPU or it's too small, you can use CPU mode:

### Windows:
```bash
set CUDA_VISIBLE_DEVICES=
python qwen_image_api.py
```

### Linux/Mac:
```bash
CUDA_VISIBLE_DEVICES='' python qwen_image_api.py
```

**Warning:** CPU mode is VERY slow (10-30+ minutes per image) but will work without GPU.

## Additional Memory Saving Tips

### 1. Reduce Image Size
Start with small sizes and increase gradually:
- Start: 512x512
- If that works: 768x768
- If that works: 1024x1024

### 2. Reduce Inference Steps
Fewer steps = less memory but slightly lower quality:
- Minimum: 15 steps (fast, lower quality)
- Recommended: 25-30 steps (good balance)
- Maximum: 50 steps (best quality, slower)

### 3. Close Other Applications
- Close browsers with many tabs
- Close other Python processes
- Close games or other GPU applications
- Restart your computer if needed

### 4. Use the Cleanup Endpoint
Between generations, call the cleanup endpoint:

```bash
curl -X POST http://localhost:8000/cleanup
```

This forces garbage collection and clears CUDA cache.

### 5. Restart the API Server
If you're getting OOM errors, restart the server:
- Stop the server (Ctrl+C)
- Wait a few seconds
- Start it again

## Troubleshooting OOM Errors

### Error: "RuntimeError: CUDA error: out of memory"

**Try these in order:**

1. **Use the Low VRAM version:**
   ```bash
   python qwen_image_api_low_vram.py
   ```

2. **Reduce image size to 512x512:**
   ```python
   requests.post("http://localhost:8000/generate", json={
       "prompt": "your prompt",
       "width": 512,
       "height": 512,
       "num_inference_steps": 20
   })
   ```

3. **Restart the server and try immediately:**
   ```bash
   # Stop server (Ctrl+C)
   # Wait 5 seconds
   python qwen_image_api_low_vram.py
   # Then immediately try generation
   ```

4. **Check what's using GPU memory:**
   ```bash
   nvidia-smi
   ```
   Kill any other processes using GPU.

5. **Try CPU mode** (slow but reliable)

## Installing xformers (Optional but Recommended)

xformers provides memory-efficient attention that can reduce VRAM usage by 20-30%:

### Windows (CUDA 11.8):
```bash
pip install xformers --index-url https://download.pytorch.org/whl/cu118
```

### Windows (CUDA 12.1):
```bash
pip install xformers --index-url https://download.pytorch.org/whl/cu121
```

### Linux:
```bash
pip install xformers
```

After installing xformers, restart the API server.

## Monitoring Memory Usage

All optimized versions show memory usage in logs:

```
INFO: GPU memory before generation: 2.34 GB
INFO: Generating image...
INFO: GPU memory after generation: 3.12 GB
```

Watch these numbers to understand your memory usage patterns.

## Still Having Issues?

If you're still getting OOM errors with the low VRAM version and minimum settings:

1. Your GPU may not have enough VRAM for this model
2. Try a smaller model (Stable Diffusion XL or SD 1.5)
3. Use CPU mode (very slow but works)
4. Consider cloud GPU services (Google Colab, Paperspace, etc.)

## Example: Start with Safe Settings

```python
import requests

# Start with the safest settings
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "a beautiful landscape",
        "width": 512,
        "height": 512,
        "num_inference_steps": 20
    }
)

# If that works, gradually increase
```

## Performance Comparison

Approximate generation times on RTX 3080 (10GB):

| Version | Size | Steps | Time | Memory |
|---------|------|-------|------|--------|
| Standard | 1024x1024 | 50 | OOM ❌ | 12GB+ |
| Optimized | 1024x1024 | 50 | OOM ❌ | 11GB+ |
| Low VRAM | 1024x1024 | 30 | ~60s ✓ | 9GB |
| Low VRAM | 768x768 | 25 | ~35s ✓ | 7GB |
| Low VRAM | 512x512 | 20 | ~20s ✓ | 6GB |

Your mileage may vary based on GPU model and other factors.
