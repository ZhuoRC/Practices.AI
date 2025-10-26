# Quick Start Guide - Qwen-Image APIs

This project provides two separate APIs:
1. **Image Generation** - Text-to-image generation
2. **Image Editing** - Edit existing images with text prompts

## TL;DR - Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
# Install PyTorch with CUDA support first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt

# For image editing support, install diffusers from git:
pip install git+https://github.com/huggingface/diffusers
```

### Step 2: Start the API

**For Image Generation (Low VRAM Version):**
```bash
python qwen_image/qwen_image_api_low_vram.py
```

**For Image Editing (Low VRAM Version):**
```bash
python qwen_image_edit/qwen_image_edit_api_low_vram.py
```

Wait for the model to load (first time will download ~20GB).

### Step 3: Use the API

**Generate an Image:**
```bash
curl -X POST "http://localhost:8011/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset", "width": 512, "height": 512}' \
  --output sunset.png
```

**Edit an Image:**
```bash
curl -X POST "http://localhost:8021/edit" \
  -F "image=@input.png" \
  -F "prompt=add vibrant sunset colors" \
  --output edited.png
```

Done! Check the generated/edited images.

---

## Detailed Setup

### 1. Check Your GPU
```bash
python check_gpu.py
```

This will show your GPU name and VRAM. Based on the output:
- **6-10GB VRAM**: Use Low VRAM versions (ports 8011/8021) ⭐ RECOMMENDED
- **12GB+ VRAM**: Use Standard versions (ports 8010/8020)
- **No GPU**: Add `CUDA_VISIBLE_DEVICES=''` before python command (very slow)

### Which API to Use?
- **Image Generation**: Creates new images from text prompts
  - Standard: `qwen_image/qwen_image_api.py` (Port 8010)
  - Low VRAM: `qwen_image/qwen_image_api_low_vram.py` (Port 8011) ⭐
- **Image Editing**: Modifies existing images based on text prompts
  - Standard: `qwen_image_edit/qwen_image_edit_api.py` (Port 8020)
  - Low VRAM: `qwen_image_edit/qwen_image_edit_api_low_vram.py` (Port 8021) ⭐

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

Choose based on your needs and GPU:

**Image Generation APIs:**
```bash
# For 6-10GB VRAM (RECOMMENDED for most users)
python qwen_image/qwen_image_api_low_vram.py    # Port 8011

# OR for 12GB+ VRAM
python qwen_image/qwen_image_api.py             # Port 8010
```

**Image Editing APIs:**
```bash
# For 6-10GB VRAM (RECOMMENDED for most users)
python qwen_image_edit/qwen_image_edit_api_low_vram.py    # Port 8021

# OR for 12GB+ VRAM
python qwen_image_edit/qwen_image_edit_api.py             # Port 8020
```

**Run Both Simultaneously:**
```bash
# Terminal 1: Generation API
python qwen_image/qwen_image_api_low_vram.py

# Terminal 2: Editing API
python qwen_image_edit/qwen_image_edit_api_low_vram.py
```

The first run will download the model (~20GB for each). This may take 10-30 minutes depending on your internet speed.

### 4. Test the API

In a new terminal, use any of these methods:

**Test Image Generation:**

Using cURL:
```bash
curl -X POST "http://localhost:8011/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute cat", "width": 512, "height": 512}' \
  --output cat.png
```

Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8011/generate",
    json={
        "prompt": "A beautiful landscape",
        "width": 512,
        "height": 512,
        "num_inference_steps": 20
    }
)

with open("landscape.png", "wb") as f:
    f.write(response.content)
```

**Test Image Editing:**

Using cURL:
```bash
curl -X POST "http://localhost:8021/edit" \
  -F "image=@input.png" \
  -F "prompt=make it more vibrant" \
  --output edited.png
```

Using Python:
```python
import requests

with open("input.png", "rb") as f:
    files = {"image": f}
    data = {"prompt": "add sunset colors", "num_inference_steps": 30}
    response = requests.post("http://localhost:8021/edit", files=files, data=data)

with open("edited.png", "wb") as f:
    f.write(response.content)
```

---

## Using the API

### Image Generation

#### Python Requests

```python
import requests

response = requests.post(
    "http://localhost:8011/generate",
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

#### cURL

```bash
curl -X POST "http://localhost:8011/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute cat", "width": 512, "height": 512}' \
  --output cat.png
```

### Image Editing

#### Python Requests

```python
import requests

# Upload file and edit
with open("original.png", "rb") as f:
    files = {"image": f}
    data = {
        "prompt": "add dramatic lighting and sunset colors",
        "num_inference_steps": 30,
        "guidance_scale": 7.5
    }
    response = requests.post("http://localhost:8021/edit", files=files, data=data)

with open("edited.png", "wb") as f:
    f.write(response.content)
```

#### cURL

```bash
curl -X POST "http://localhost:8021/edit" \
  -F "image=@original.png" \
  -F "prompt=add dramatic sunset" \
  --output edited.png
```

### Interactive Documentation

Open your browser and go to:
- **Generation API:** http://localhost:8011/docs
- **Editing API:** http://localhost:8021/docs

This provides a nice UI to test the APIs!

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
# For generation
python qwen_image/qwen_image_api_low_vram.py

# For editing
python qwen_image_edit/qwen_image_edit_api_low_vram.py
```

**Solution 2:** Reduce image size
```python
{"width": 512, "height": 512, "num_inference_steps": 20}
```

**Solution 3:** Use the cleanup endpoint (Low VRAM only)
```bash
curl -X POST "http://localhost:8011/cleanup"  # For generation
curl -X POST "http://localhost:8021/cleanup"  # For editing
```

**Solution 4:** Restart and try immediately
```bash
# Stop server (Ctrl+C), wait 5 seconds, then:
python qwen_image/qwen_image_api_low_vram.py
# Immediately test with minimal settings
```

**Solution 5:** Check what's using GPU
```bash
nvidia-smi
```
Kill other GPU processes if needed.

### "Model not loaded" (503 error)

Wait for the model to finish loading. Check the server logs.

### "Connection refused"

Make sure the correct API server is running:
```bash
# For generation
python qwen_image/qwen_image_api_low_vram.py

# For editing
python qwen_image_edit/qwen_image_edit_api_low_vram.py
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

### Image Generation API (Ports 8010/8011)

#### GET /
Get API information

#### GET /health
Check server health and memory stats

#### POST /generate
Generate an image from text

**Required:**
- `prompt`: Text description

**Optional:**
- `width`: 256-2048 (default: 1024 standard, 768 low VRAM)
- `height`: 256-2048 (default: 1024 standard, 768 low VRAM)
- `num_inference_steps`: 10-100 (default: 50 standard, 10 low VRAM)
- `true_cfg_scale`: 1.0-20.0 (default: 4.0)
- `seed`: Integer for reproducibility
- `negative_prompt`: What to avoid (default: " ")
- `enhance_prompt`: Add quality enhancement (default: true)
- `return_base64`: Return base64 instead of binary (default: false)

#### POST /cleanup (Low VRAM version only)
Force memory cleanup

#### GET /docs
Interactive API documentation

### Image Editing API (Ports 8020/8021)

#### GET /
Get API information

#### GET /health
Check server health and memory stats

#### POST /edit
Edit an image based on text prompt

**Required:**
- `prompt`: Text description of desired edits
- `image` OR `image_base64`: Input image (file upload or base64)

**Optional:**
- `width`: Output width (default: keep original)
- `height`: Output height (default: keep original)
- `num_inference_steps`: 10-100 (default: 50 standard, 30 low VRAM)
- `guidance_scale`: 1.0-20.0 (default: 7.5)
- `seed`: Integer for reproducibility
- `negative_prompt`: What to avoid (default: "blurry, distorted...")
- `return_base64`: Return base64 instead of binary (default: false)

#### POST /cleanup (Low VRAM version only)
Force memory cleanup

#### GET /docs
Interactive API documentation

---

## File Structure

```
qwen_image/                           # Image Generation APIs
├── qwen_image_api.py                # Standard version (Port 8010)
└── qwen_image_api_low_vram.py       # Low VRAM version (Port 8011) ⭐

qwen_image_edit/                      # Image Editing APIs
├── qwen_image_edit_api.py           # Standard version (Port 8020)
└── qwen_image_edit_api_low_vram.py  # Low VRAM version (Port 8021) ⭐

api/                                  # Shared utilities (future use)

docs/                                 # Documentation
├── API_USAGE.md                     # Full API documentation
├── QUICK_START.md                   # This file
├── MEMORY_GUIDE.md                  # Memory optimization guide
└── IMAGE_EDIT_GUIDE.md              # Image editing guide

check_gpu.py                          # GPU diagnostic tool
requirements.txt                      # Dependencies
images/                               # Generated/edited images saved here
├── qwen-image/                      # Images from standard generation API
├── qwen-image-low-vram/             # Images from low VRAM generation API
├── qwen-image-edit/                 # Images from standard editing API
└── qwen-image-edit-low-vram/        # Images from low VRAM editing API
```

⭐ = Recommended for most users (6-10GB VRAM)

**Note:** Generated and edited images are automatically organized into model-specific subfolders.

---

## Next Steps

1. ✅ Start with the low VRAM versions (ports 8011/8021)
2. ✅ Test with safe settings (512x512, 20-30 steps)
3. ✅ Gradually increase if it works
4. 📖 Read MEMORY_GUIDE.md if you have memory issues
5. 📖 Read API_USAGE.md for detailed API documentation
6. 📖 Read IMAGE_EDIT_GUIDE.md for image editing tips

---

## Getting Help

1. **Out of memory errors**: See MEMORY_GUIDE.md
2. **API usage questions**: See API_USAGE.md
3. **Image editing tips**: See IMAGE_EDIT_GUIDE.md
4. **Model information**: https://github.com/QwenLM/Qwen-Image
5. **General issues**: Check server logs for details

---

## Example Workflows

### Image Generation Workflow

```bash
# Terminal 1: Start generation server
python qwen_image/qwen_image_api_low_vram.py

# Terminal 2: Wait for "Model loaded successfully!", then test
curl -X POST "http://localhost:8011/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A magical forest", "width": 768, "height": 768}' \
  --output forest.png

# Check the generated forest.png!
```

### Image Editing Workflow

```bash
# Terminal 1: Start editing server
python qwen_image_edit/qwen_image_edit_api_low_vram.py

# Terminal 2: Wait for "Model loaded successfully!", then test
curl -X POST "http://localhost:8021/edit" \
  -F "image=@forest.png" \
  -F "prompt=add sunset lighting and make it more dramatic" \
  --output forest_edited.png

# Check the edited forest_edited.png!
```

### Running Both APIs Together

```bash
# Terminal 1: Start generation API
python qwen_image/qwen_image_api_low_vram.py

# Terminal 2: Start editing API
python qwen_image_edit/qwen_image_edit_api_low_vram.py

# Terminal 3: Generate, then edit!
# Generate
curl -X POST "http://localhost:8011/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat", "width": 512, "height": 512}' \
  --output cat.png

# Edit
curl -X POST "http://localhost:8021/edit" \
  -F "image=@cat.png" \
  -F "prompt=add a wizard hat" \
  --output cat_wizard.png
```

**Using Python:**
```python
import requests

# Generate an image
gen_response = requests.post('http://localhost:8011/generate',
    json={'prompt': 'a magical forest', 'width': 768, 'height': 768})

with open('forest.png', 'wb') as f:
    f.write(gen_response.content)

# Edit the generated image
with open('forest.png', 'rb') as f:
    edit_response = requests.post('http://localhost:8021/edit',
        files={'image': f},
        data={'prompt': 'add sunset lighting'})

with open('forest_sunset.png', 'wb') as f:
    f.write(edit_response.content)

# Check both images!
```

---

**Enjoy generating and editing images with Qwen-Image! 🎨✨**
