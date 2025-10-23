# Quick Start Guide - Qwen-Image API

## TL;DR - Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install git+https://github.com/huggingface/diffusers
pip install -r requirements_api.txt
```

### Step 2: Start the API (Low VRAM Version)
```bash
python qwen_image_api_low_vram.py
```

Wait for the model to load (first time will download ~20GB).

### Step 3: Generate an Image
```bash
python test_api_low_vram.py
```

Done! Check the generated images in the current directory.

---

## Detailed Setup

### 1. Check Your GPU
```bash
python check_gpu.py
```

This will show your GPU name and VRAM. Based on the output:
- **6-10GB VRAM**: Use `qwen_image_api_low_vram.py` ⭐ RECOMMENDED
- **10-16GB VRAM**: Use `qwen_image_api_optimized.py`
- **16GB+ VRAM**: Use `qwen_image_api.py`
- **No GPU**: Add `CUDA_VISIBLE_DEVICES=''` before python command (very slow)

### 2. Install xformers (Optional but Recommended)

This can reduce memory usage by 20-30%:

**For CUDA 11.8:**
```bash
pip install xformers --index-url https://download.pytorch.org/whl/cu118
```

**For CUDA 12.1:**
```bash
pip install xformers --index-url https://download.pytorch.org/whl/cu121
```

### 3. Start the Appropriate API Server

Choose based on your GPU:

```bash
# For 6-10GB VRAM (RECOMMENDED for most users)
python qwen_image_api_low_vram.py

# OR for 10-16GB VRAM
python qwen_image_api_optimized.py

# OR for 16GB+ VRAM
python qwen_image_api.py
```

The first run will download the model (~20GB). This may take 10-30 minutes depending on your internet speed.

### 4. Test the API

In a new terminal:

```bash
# Run the low VRAM test (safe settings)
python test_api_low_vram.py

# OR run the full test (may cause OOM on small GPUs)
python test_api_client.py
```

---

## Using the API

### Method 1: Python Requests

```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "A beautiful sunset over mountains",
        "width": 768,
        "height": 768,
        "num_inference_steps": 25,
        "seed": 42
    }
)

with open("my_image.png", "wb") as f:
    f.write(response.content)
```

### Method 2: cURL

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute cat", "width": 512, "height": 512}' \
  --output cat.png
```

### Method 3: Interactive Documentation

Open your browser and go to: **http://localhost:8000/docs**

This provides a nice UI to test the API!

---

## Safe Settings to Start With

If you're getting out-of-memory errors, start with these safe settings:

```python
{
    "prompt": "Your prompt here",
    "width": 512,        # Small size
    "height": 512,       # Small size
    "num_inference_steps": 20,  # Fewer steps
    "seed": 42          # Optional: for reproducibility
}
```

Once this works, gradually increase:
1. Try 768x768
2. Then try 1024x1024
3. Increase steps to 30, then 40

---

## Common Issues

### "CUDA out of memory"

**Solution 1:** Use the low VRAM version
```bash
python qwen_image_api_low_vram.py
```

**Solution 2:** Reduce image size
```python
{"width": 512, "height": 512, "num_inference_steps": 20}
```

**Solution 3:** Restart and try immediately
```bash
# Stop server (Ctrl+C), wait 5 seconds, then:
python qwen_image_api_low_vram.py
# Immediately test with minimal settings
```

**Solution 4:** Check what's using GPU
```bash
nvidia-smi
```
Kill other GPU processes if needed.

### "Model not loaded" (503 error)

Wait for the model to finish loading. Check the server logs.

### "Connection refused"

Make sure the API server is running:
```bash
python qwen_image_api_low_vram.py
```

### Server is very slow

This is normal for:
- First-time model download
- CPU mode (use GPU if possible)
- Large images (1024x1024+)
- Many inference steps (50+)

Expected speeds:
- GPU (low VRAM mode): 20-60 seconds per image
- GPU (standard mode): 10-30 seconds per image
- CPU: 5-30+ minutes per image

---

## API Endpoints

### GET /
Get API information

### GET /health
Check server health and memory stats

### POST /generate
Generate an image

**Required:**
- `prompt`: Text description

**Optional:**
- `width`: 256-2048 (default: varies by version)
- `height`: 256-2048 (default: varies by version)
- `num_inference_steps`: 10-100 (default: varies by version)
- `true_cfg_scale`: 1.0-20.0 (default: 4.0)
- `seed`: Integer for reproducibility
- `negative_prompt`: What to avoid (default: " ")
- `enhance_prompt`: Add quality enhancement (default: true)
- `return_base64`: Return base64 instead of binary (default: false)

### POST /cleanup (Low VRAM version only)
Force memory cleanup

### GET /docs
Interactive API documentation

---

## File Structure

```
qwen_image_api.py              # Standard version (16GB+ VRAM)
qwen_image_api_optimized.py    # Optimized version (10-16GB VRAM)
qwen_image_api_low_vram.py     # Low VRAM version (6-10GB VRAM) ⭐
test_api_client.py             # Full test client
test_api_low_vram.py           # Safe test client ⭐
check_gpu.py                   # GPU diagnostic tool
requirements_api.txt           # Dependencies
API_USAGE.md                   # Full API documentation
MEMORY_GUIDE.md                # Memory optimization guide
QUICK_START.md                 # This file
```

⭐ = Recommended for most users

---

## Next Steps

1. ✅ Start with the low VRAM version
2. ✅ Test with safe settings (512x512, 20 steps)
3. ✅ Gradually increase if it works
4. 📖 Read MEMORY_GUIDE.md if you have issues
5. 📖 Read API_USAGE.md for detailed API documentation

---

## Getting Help

1. **Out of memory errors**: See MEMORY_GUIDE.md
2. **API usage questions**: See API_USAGE.md
3. **Model information**: https://github.com/QwenLM/Qwen-Image
4. **General issues**: Check server logs for details

---

## Example Workflow

```bash
# Terminal 1: Start server
python qwen_image_api_low_vram.py

# Terminal 2: Wait for "Model loaded successfully!", then test
python test_api_low_vram.py

# If successful, try your own prompts:
python -c "
import requests
r = requests.post('http://localhost:8000/generate',
    json={'prompt': 'a magical forest', 'width': 768, 'height': 768})
open('forest.png', 'wb').write(r.content)
"

# Check the generated forest.png!
```

---

**Enjoy generating images with Qwen-Image! 🎨**
