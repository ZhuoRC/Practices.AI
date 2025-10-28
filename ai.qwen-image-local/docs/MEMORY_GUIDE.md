# Memory Optimization Guide for Qwen-Image APIs

## Overview

This guide covers memory optimization for both Qwen-Image APIs:
1. **Image Generation** - Text-to-image generation using Qwen/Qwen-Image
2. **Image Editing** - Image editing using Qwen/Qwen-Image-Edit-2509

Both models are 20B parameter models that require significant GPU memory (VRAM). If you're getting "CUDA out of memory" errors, you need to use the low-VRAM optimized versions.

## Which Version Should I Use?

### Image Generation APIs

#### 1. Standard Version - `qwen_image/qwen_image_api.py`
**For: GPUs with 12-16GB+ VRAM**
**Port: 8010**

```bash
python qwen_image/qwen_image_api.py
```

**Pros:**
- Faster generation speed
- Supports full resolution (up to 2048x2048)
- Default: 1024x1024, 50 steps

**Cons:**
- Requires 12-16GB+ VRAM
- Will OOM on smaller GPUs

---

#### 2. Low VRAM Version - `qwen_image/qwen_image_api_low_vram.py` ⭐
**For: GPUs with 6-10GB VRAM**
**Port: 8011**
**RECOMMENDED FOR MOST USERS**

```bash
python qwen_image/qwen_image_api_low_vram.py
```

**Optimizations:**
- Sequential CPU offload (most aggressive)
- Aggressive attention slicing (slice_size=1)
- VAE slicing (tiling disabled for compatibility)
- BFloat16 precision (better numerical stability)
- Automatic memory cleanup
- Lower defaults (768x768, 10 steps)

**Pros:**
- Works on 6-8GB GPUs
- Detailed logging and error messages
- Automatic memory management
- `/cleanup` endpoint for manual memory cleanup

**Cons:**
- Slower generation (components move between CPU/GPU)
- Recommended max resolution: 1024x1024

---

### Image Editing APIs

#### 1. Standard Version - `qwen_image_edit/qwen_image_edit_api.py`
**For: GPUs with 12-16GB+ VRAM**
**Port: 8020**

```bash
python qwen_image_edit/qwen_image_edit_api.py
```

**Pros:**
- Faster editing speed
- Supports full resolution (up to 2048x2048)
- Default: 50 inference steps

**Cons:**
- Requires 12-16GB+ VRAM
- Will OOM on smaller GPUs

---

#### 2. Low VRAM Version - `qwen_image_edit/qwen_image_edit_api_low_vram.py` ⭐
**For: GPUs with 6-10GB VRAM**
**Port: 8021**
**RECOMMENDED FOR MOST USERS**

```bash
python qwen_image_edit/qwen_image_edit_api_low_vram.py
```

**Optimizations:**
- Sequential CPU offload (most aggressive)
- Aggressive attention slicing (slice_size=1)
- VAE slicing
- BFloat16 precision
- Automatic memory cleanup
- Lower defaults (30 inference steps)
- Input validation and size warnings

**Pros:**
- Works on 6-8GB GPUs
- Detailed logging and error handling
- Automatic memory management
- `/cleanup` endpoint for manual memory cleanup

**Cons:**
- Slower editing (components move between CPU/GPU)
- Recommended max resolution: 1024x1024

---

## Quick Decision Chart

```
Your GPU VRAM:

For Image Generation:
├─ 12GB+     → Use qwen_image/qwen_image_api.py (Port 8010)
└─ 6-10GB    → Use qwen_image/qwen_image_api_low_vram.py (Port 8011) ⭐

For Image Editing:
├─ 12GB+     → Use qwen_image_edit/qwen_image_edit_api.py (Port 8020)
└─ 6-10GB    → Use qwen_image_edit/qwen_image_edit_api_low_vram.py (Port 8021) ⭐

For <6GB VRAM → Use CPU mode (see below)
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

### Image Generation Settings

#### 12-16GB+ VRAM (Standard - Port 8010)
```python
{
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 50,
    "true_cfg_scale": 4.0
}
```

#### 8-12GB VRAM (Low VRAM - Port 8011)
```python
{
    "width": 768,
    "height": 768,
    "num_inference_steps": 30,
    "true_cfg_scale": 4.0
}
```

#### 6-8GB VRAM (Low VRAM - Port 8011)
```python
{
    "width": 512,
    "height": 512,
    "num_inference_steps": 20,
    "true_cfg_scale": 4.0
}
```

### Image Editing Settings

#### 12-16GB+ VRAM (Standard - Port 8020)
```python
{
    "width": 1024,  # or None to keep original size
    "height": 1024,
    "num_inference_steps": 50,
    "guidance_scale": 7.5
}
```

#### 8-12GB VRAM (Low VRAM - Port 8021)
```python
{
    "width": 768,  # or None to keep original size
    "height": 768,
    "num_inference_steps": 30,
    "guidance_scale": 7.5
}
```

#### 6-8GB VRAM (Low VRAM - Port 8021)
```python
{
    "width": 512,  # or None to keep original size
    "height": 512,
    "num_inference_steps": 20,
    "guidance_scale": 7.5
}
```

## CPU Mode (No GPU)

If you don't have a GPU or it's too small, you can use CPU mode:

### Windows:
```bash
# For Image Generation
set CUDA_VISIBLE_DEVICES=
python qwen_image/qwen_image_api.py

# For Image Editing
set CUDA_VISIBLE_DEVICES=
python qwen_image_edit/qwen_image_edit_api.py
```

### Linux/Mac:
```bash
# For Image Generation
CUDA_VISIBLE_DEVICES='' python qwen_image/qwen_image_api.py

# For Image Editing
CUDA_VISIBLE_DEVICES='' python qwen_image_edit/qwen_image_edit_api.py
```

**Warning:** CPU mode is VERY slow (10-30+ minutes per image for generation, 5-15+ minutes for editing) but will work without GPU.

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

### 4. Use the Cleanup Endpoint (Low VRAM Versions Only)
Between operations, call the cleanup endpoint to force garbage collection:

**For Image Generation (Low VRAM):**
```bash
curl -X POST http://localhost:8011/cleanup
```

**For Image Editing (Low VRAM):**
```bash
curl -X POST http://localhost:8021/cleanup
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
   # For Generation
   python qwen_image/qwen_image_api_low_vram.py

   # For Editing
   python qwen_image_edit/qwen_image_edit_api_low_vram.py
   ```

2. **Reduce image size to 512x512:**

   **For Generation:**
   ```python
   requests.post("http://localhost:8011/generate", json={
       "prompt": "your prompt",
       "width": 512,
       "height": 512,
       "num_inference_steps": 20
   })
   ```

   **For Editing:**
   ```python
   with open("image.png", "rb") as f:
       requests.post("http://localhost:8021/edit",
           files={"image": f},
           data={
               "prompt": "your edit prompt",
               "width": 512,
               "height": 512,
               "num_inference_steps": 20
           })
   ```

3. **Restart the server and try immediately:**
   ```bash
   # Stop server (Ctrl+C)
   # Wait 5 seconds
   python qwen_image/qwen_image_api_low_vram.py  # or qwen_image_edit/...
   # Then immediately try your operation
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

### Image Generation Example
```python
import requests

# Start with the safest settings (Low VRAM version on port 8011)
response = requests.post(
    "http://localhost:8011/generate",
    json={
        "prompt": "a beautiful landscape",
        "width": 512,
        "height": 512,
        "num_inference_steps": 20
    }
)

with open("output.png", "wb") as f:
    f.write(response.content)

# If that works, gradually increase size and steps
```

### Image Editing Example
```python
import requests

# Start with the safest settings (Low VRAM version on port 8021)
with open("input.png", "rb") as f:
    response = requests.post(
        "http://localhost:8021/edit",
        files={"image": f},
        data={
            "prompt": "enhance colors",
            "width": 512,
            "height": 512,
            "num_inference_steps": 20
        }
    )

with open("edited.png", "wb") as f:
    f.write(response.content)

# If that works, gradually increase size and steps
```

## Performance Comparison

Approximate times on RTX 3080 (10GB VRAM):

### Image Generation
| Version | Size | Steps | Time | Memory | Port |
|---------|------|-------|------|--------|------|
| Standard | 1024x1024 | 50 | OOM ❌ | 12GB+ | 8010 |
| Low VRAM | 1024x1024 | 30 | ~60s ✓ | 9GB | 8011 |
| Low VRAM | 768x768 | 25 | ~35s ✓ | 7GB | 8011 |
| Low VRAM | 512x512 | 20 | ~20s ✓ | 6GB | 8011 |

### Image Editing
| Version | Size | Steps | Time | Memory | Port |
|---------|------|-------|------|--------|------|
| Standard | 1024x1024 | 50 | OOM ❌ | 12GB+ | 8020 |
| Low VRAM | 1024x1024 | 30 | ~50s ✓ | 9GB | 8021 |
| Low VRAM | 768x768 | 25 | ~30s ✓ | 7GB | 8021 |
| Low VRAM | 512x512 | 20 | ~15s ✓ | 6GB | 8021 |

*Note: Actual performance varies based on GPU model, prompt complexity, and system configuration.*

## Running Multiple APIs Simultaneously

You can run both Generation and Editing APIs at the same time since they use different ports:

```bash
# Terminal 1: Image Generation (Low VRAM)
python qwen_image/qwen_image_api_low_vram.py

# Terminal 2: Image Editing (Low VRAM)
python qwen_image_edit/qwen_image_edit_api_low_vram.py
```

**Memory consideration:** Running both APIs simultaneously will require approximately:
- **Standard versions together**: 24-32GB VRAM
- **Low VRAM versions together**: 12-18GB VRAM (with sequential offload)
- **One of each**: 18-24GB VRAM

For most users with 10GB or less VRAM, it's recommended to run only one API at a time.
