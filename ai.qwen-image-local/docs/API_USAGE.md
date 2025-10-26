# Qwen-Image RESTful API

A RESTful API server for text-to-image generation and image editing using Qwen-Image models.

This project provides two separate API servers:
1. **Image Generation API** - Text-to-image generation using Qwen/Qwen-Image
2. **Image Editing API** - Image editing using Qwen/Qwen-Image-Edit-2509

## Features

### Image Generation API
- Text-to-image generation using Qwen/Qwen-Image model
- Support for both GPU and CPU execution
- Configurable image dimensions, inference steps, and guidance scale
- Automatic prompt enhancement for better results
- Support for reproducible generation with seed values
- Multiple response formats (binary image or base64)
- Low VRAM version for GPUs with 6-8GB memory

### Image Editing API
- Image editing using Qwen/Qwen-Image-Edit-2509 model
- Edit images based on text prompts
- Support for multipart file upload or base64 image input
- Configurable output dimensions and editing parameters
- Reproducible edits with seed values
- Low VRAM version optimized for limited GPU memory

### Common Features
- Built with FastAPI for high performance and automatic documentation
- Automatic image saving to model-specific folders (organized by API type)
- Health check endpoints with GPU memory statistics
- Separate ports for each service (can run simultaneously)

## Installation

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Linux/Mac
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
pip install -r requirements.txt

# Optional: Install xformers for memory efficiency (20-30% VRAM reduction)
pip install xformers --no-deps
```

### 3. GPU Setup (Optional but Recommended)

For GPU support, ensure you have:
- NVIDIA GPU with CUDA support
- NVIDIA drivers installed
- PyTorch with CUDA support

Check your GPU setup:
```bash
python check_gpu.py
```

## Usage

### Starting the API Servers

You can run the generation and editing APIs independently or simultaneously.

#### Image Generation API (Standard)
```bash
python qwen_image/qwen_image_api.py
```
Server starts on `http://localhost:8010`

#### Image Generation API (Low VRAM)
```bash
python qwen_image/qwen_image_api_low_vram.py
```
Server starts on `http://localhost:8011`

#### Image Editing API (Standard)
```bash
python qwen_image_edit/qwen_image_edit_api.py
```
Server starts on `http://localhost:8020`

#### Image Editing API (Low VRAM)
```bash
python qwen_image_edit/qwen_image_edit_api_low_vram.py
```
Server starts on `http://localhost:8021`

**Note:** On first run, each API will download its respective model (~20GB for each), which may take some time.

### API Endpoints

## Image Generation API

Endpoints for text-to-image generation (available on ports 8010 and 8011)

#### 1. Root Endpoint
```
GET http://localhost:8010/
```
Returns API information and available endpoints.

#### 2. Health Check
```
GET http://localhost:8010/health
```
Check if the server is running and model is loaded.

#### 3. Generate Image
```
POST http://localhost:8010/generate
```

**Request Body (JSON):**
```json
{
  "prompt": "A serene landscape with mountains and a lake at sunset",
  "negative_prompt": " ",
  "width": 1024,
  "height": 1024,
  "num_inference_steps": 50,
  "true_cfg_scale": 4.0,
  "seed": 42,
  "enhance_prompt": true,
  "return_base64": false
}
```

**Parameters:**
- `prompt` (required): Text description of the image to generate
- `negative_prompt` (optional): Negative prompt (default: " ")
- `width` (optional): Image width in pixels (256-2048, default: 1024)
- `height` (optional): Image height in pixels (256-2048, default: 1024)
- `num_inference_steps` (optional): Number of denoising steps (1-100, default: 50)
- `true_cfg_scale` (optional): Guidance scale (1.0-20.0, default: 4.0)
- `seed` (optional): Random seed for reproducibility (default: None)
- `enhance_prompt` (optional): Add quality enhancement to prompt (default: true)
- `return_base64` (optional): Return image as base64 string instead of binary (default: false)

**Response:**
- If `return_base64=false`: Returns binary PNG image data
- If `return_base64=true`: Returns JSON with base64-encoded image

#### 4. Interactive API Documentation
```
GET http://localhost:8010/docs
```
FastAPI provides automatic interactive documentation where you can test the API.

## Image Editing API

Endpoints for image editing (available on ports 8020 and 8021)

#### 1. Root Endpoint
```
GET http://localhost:8020/
```
Returns API information and available endpoints.

#### 2. Health Check
```
GET http://localhost:8020/health
```
Check if the server is running and model is loaded. Includes GPU memory statistics.

#### 3. Edit Image
```
POST http://localhost:8020/edit
```

**Request Format:** Multipart form data

**Parameters:**
- `prompt` (required): Text description of desired edits
- `image` (conditional): Input image file (required if image_base64 not provided)
- `image_base64` (conditional): Input image as base64 string (required if image not provided)
- `negative_prompt` (optional): Negative prompt (default: "blurry, distorted, low quality, artifacts")
- `width` (optional): Output image width (default: keep original size)
- `height` (optional): Output image height (default: keep original size)
- `num_inference_steps` (optional): Number of denoising steps (default: 50 for standard, 30 for low VRAM)
- `guidance_scale` (optional): Guidance scale (1.0-20.0, default: 7.5)
- `seed` (optional): Random seed for reproducibility
- `return_base64` (optional): Return image as base64 string instead of binary (default: false)

**Response:**
- If `return_base64=false`: Returns binary PNG image data
- If `return_base64=true`: Returns JSON with base64-encoded image

#### 4. Cleanup Memory (Low VRAM Only)
```
POST http://localhost:8021/cleanup
```
Force aggressive GPU memory cleanup (only available in low VRAM version).

#### 5. Interactive API Documentation
```
GET http://localhost:8020/docs
```
FastAPI provides automatic interactive documentation where you can test the API.

## Example Usage

### Image Generation Examples

#### Using Python Requests

```python
import requests

# Simple example
response = requests.post(
    "http://localhost:8010/generate",
    json={
        "prompt": "A beautiful sunset over the ocean",
        "width": 1280,
        "height": 720,
        "num_inference_steps": 30
    }
)

# Save the image
if response.status_code == 200:
    with open("sunset.png", "wb") as f:
        f.write(response.content)
    print("Image saved as sunset.png")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

#### Using Python with Base64 Response

```python
import requests
import base64
from PIL import Image
import io

response = requests.post(
    "http://localhost:8010/generate",
    json={
        "prompt": "A cute robot",
        "width": 768,
        "height": 768,
        "return_base64": True
    }
)

if response.status_code == 200:
    data = response.json()
    if data["success"]:
        # Decode base64 and save
        img_data = base64.b64decode(data["image_base64"])
        image = Image.open(io.BytesIO(img_data))
        image.save("robot.png")
        print("Image saved as robot.png")
```

#### Using cURL

```bash
# Generate an image and save it
curl -X POST "http://localhost:8010/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cute cat playing with a ball of yarn",
    "width": 1024,
    "height": 1024,
    "seed": 42
  }' \
  --output cat.png
```

### Image Editing Examples

#### Using Python with File Upload

```python
import requests

# Edit an image by uploading a file
with open("input_image.png", "rb") as f:
    files = {"image": f}
    data = {
        "prompt": "make the sky more dramatic and add sunset colors",
        "guidance_scale": 7.5,
        "num_inference_steps": 50
    }

    response = requests.post(
        "http://localhost:8020/edit",
        files=files,
        data=data
    )

if response.status_code == 200:
    with open("edited_image.png", "wb") as f:
        f.write(response.content)
    print("Edited image saved as edited_image.png")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

#### Using Python with Base64 Input

```python
import requests
import base64
from PIL import Image
import io

# Read and encode input image
with open("input_image.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8020/edit",
    data={
        "image_base64": img_base64,
        "prompt": "change the background to a forest",
        "num_inference_steps": 50,
        "return_base64": True
    }
)

if response.status_code == 200:
    data = response.json()
    if data["success"]:
        # Decode and save edited image
        img_data = base64.b64decode(data["image_base64"])
        image = Image.open(io.BytesIO(img_data))
        image.save("edited_image.png")
        print("Edited image saved")
```

#### Using cURL for Image Editing

```bash
# Edit an image using file upload
curl -X POST "http://localhost:8020/edit" \
  -F "image=@input_image.png" \
  -F "prompt=add vibrant colors and enhance details" \
  -F "num_inference_steps=50" \
  --output edited_image.png
```



## Supported Aspect Ratios

The model supports various aspect ratios:
- 1:1 (1024x1024)
- 16:9 (1280x720)
- 9:16 (720x1280)
- 4:3 (1024x768)
- 3:4 (768x1024)
- 3:2 (1152x768)
- 2:3 (768x1152)

## Prompt Enhancement

When `enhance_prompt=true` (default), the API automatically adds quality enhancement suffixes:
- English prompts: ", Ultra HD, 4K, cinematic composition."
- Chinese prompts: ", 超清，4K，电影级构图."

This typically improves image quality and detail.

## Performance Tips

1. **Use GPU**: Generation is much faster on GPU (~20-30s) vs CPU (several minutes)
2. **Adjust inference steps**: More steps = better quality but slower (50 is a good balance)
3. **Batch processing**: Generate multiple images by making parallel API calls
4. **Use seeds**: For reproducible results, use the same seed value

## Troubleshooting

### Model Download Issues
If the model fails to download, you may need to:
1. Check your internet connection
2. Ensure you have enough disk space (~20GB)
3. Set up Hugging Face authentication if needed

### Out of Memory (OOM) Errors
If you get OOM errors on GPU:
1. Use the Low VRAM versions (ports 8011 for generation, 8021 for editing)
2. Close other GPU-intensive applications
3. Reduce image dimensions (try 768x768 or smaller)
4. Reduce `num_inference_steps` (20-30 instead of 50)
5. Standard versions require ~12-16GB VRAM; Low VRAM versions work with 6-8GB

### Slow Generation/Editing
If operations are slow:
1. Check if GPU is being used (see server logs)
2. Reduce `num_inference_steps` (try 30-40)
3. Use smaller image dimensions
4. Ensure you're not running Low VRAM version when you have sufficient memory

### Image Editing Issues
If edits don't match your prompt:
1. Increase `guidance_scale` (try 10-15)
2. Increase `num_inference_steps` (try 50-70)
3. Be more specific in your prompt
4. Try different seeds for variations

## API Server Configuration

### Changing Ports and Host

To change the host or port, modify the `uvicorn.run()` call in the respective API file:

**Generation API** (`qwen_image/qwen_image_api.py`):
```python
uvicorn.run(
    app,
    host="0.0.0.0",  # Listen on all interfaces
    port=8010,       # Default generation port
    log_level="info"
)
```

**Editing API** (`qwen_image_edit/qwen_image_edit_api.py`):
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8020,       # Default editing port
    log_level="info"
)
```

Or run with uvicorn directly:

```bash
# Generation API
uvicorn qwen_image.qwen_image_api:app --host 0.0.0.0 --port 8010 --reload

# Editing API
uvicorn qwen_image_edit.qwen_image_edit_api:app --host 0.0.0.0 --port 8020 --reload
```

### Running Multiple APIs Simultaneously

You can run both generation and editing APIs at the same time since they use different ports:

```bash
# Terminal 1: Start generation API
python qwen_image/qwen_image_api.py

# Terminal 2: Start editing API
python qwen_image_edit/qwen_image_edit_api.py
```

## Model Information

### Image Generation Model
- **Model**: Qwen/Qwen-Image
- **Type**: 20B MMDiT foundation model
- **Size**: ~20GB
- **Capabilities**: Text-to-image generation
- **Repository**: https://github.com/QwenLM/Qwen-Image
- **License**: Check the model repository for license details

### Image Editing Model
- **Model**: Qwen/Qwen-Image-Edit-2509
- **Type**: Based on 20B Qwen-Image foundation
- **Size**: ~20GB
- **Capabilities**: Image editing with text prompts, multi-image input support
- **Repository**: https://github.com/QwenLM/Qwen-Image
- **License**: Check the model repository for license details

### Port Assignments
- **Generation (Standard)**: 8010
- **Generation (Low VRAM)**: 8011
- **Editing (Standard)**: 8020
- **Editing (Low VRAM)**: 8021

### Image Storage Locations

All generated and edited images are automatically saved with timestamps to model-specific folders:

- **Generation (Standard)**: `images/qwen-image/generated_YYYYMMDD_HHMMSS.png`
- **Generation (Low VRAM)**: `images/qwen-image-low-vram/generated_YYYYMMDD_HHMMSS.png`
- **Editing (Standard)**: `images/qwen-image-edit/edited_YYYYMMDD_HHMMSS.png`
- **Editing (Low VRAM)**: `images/qwen-image-edit-low-vram/edited_YYYYMMDD_HHMMSS.png`

This organization makes it easy to track which model version produced each image.

## License

This API wrapper is provided as-is. Please check the Qwen-Image model license for usage terms.
