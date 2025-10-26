# Qwen-Image RESTful API

A RESTful API server for text-to-image generation using the Qwen-Image model.

## Features

- Text-to-image generation using Qwen/Qwen-Image model
- Support for both GPU and CPU execution
- Configurable image dimensions, inference steps, and guidance scale
- Automatic prompt enhancement for better results
- Support for reproducible generation with seed values
- Multiple response formats (binary image or base64)
- Built with FastAPI for high performance and automatic documentation

## Installation

python -m venv .venv

### 1. Install Dependencies

First, install the required packages:

```bash
# Install the latest diffusers from GitHub
pip install git+https://github.com/huggingface/diffusers


# Step 1: 先装 PyTorch 生态
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Step 2: 再强制装 xformers，不检查依赖
pip install xformers==0.0.27 --no-deps

# Install other requirements
pip install -r requirements_api.txt

```

### 2. GPU Setup (Optional but Recommended)

For GPU support, ensure you have:
- NVIDIA GPU with CUDA support
- NVIDIA drivers installed
- PyTorch with CUDA support

Check your GPU setup:
```bash
python check_gpu.py
```

## Usage

### Starting the API Server

Run the API server:

```bash
python qwen_image_api.py
```

The server will start on `http://localhost:8000`

On first run, it will download the Qwen-Image model (~20GB), which may take some time.

### API Endpoints

#### 1. Root Endpoint
```
GET http://localhost:8000/
```
Returns API information and available endpoints.

#### 2. Health Check
```
GET http://localhost:8000/health
```
Check if the server is running and model is loaded.

#### 3. Generate Image
```
POST http://localhost:8000/generate
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
GET http://localhost:8000/docs
```
FastAPI provides automatic interactive documentation where you can test the API.

## Example Usage

### Using Python Requests

```python
import requests

# Simple example
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "A beautiful sunset over the ocean",
        "width": 1280,
        "height": 720
    }
)

# Save the image
with open("sunset.png", "wb") as f:
    f.write(response.content)
```

### Using cURL

```bash
# Generate an image and save it
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cute cat playing with a ball of yarn",
    "width": 1024,
    "height": 1024,
    "seed": 42
  }' \
  --output cat.png
```

### Using the Test Client

Run the included test client:

```bash
python test_api_client.py
```

This will generate several example images demonstrating different features.

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
1. Close other GPU-intensive applications
2. Reduce image dimensions
3. The model requires ~12-16GB VRAM for optimal performance

### Slow Generation
If generation is slow:
1. Check if GPU is being used (see server logs)
2. Reduce `num_inference_steps` (try 30-40)
3. Use smaller image dimensions

## API Server Configuration

To change the host or port, modify the `uvicorn.run()` call in `qwen_image_api.py`:

```python
uvicorn.run(
    app,
    host="0.0.0.0",  # Listen on all interfaces
    port=8000,       # Change port here
    log_level="info"
)
```

Or run with uvicorn directly:

```bash
uvicorn qwen_image_api:app --host 0.0.0.0 --port 8000 --reload
```

## Model Information

- **Model**: Qwen/Qwen-Image
- **Type**: 20B MMDiT foundation model
- **Size**: ~20GB
- **Repository**: https://github.com/QwenLM/Qwen-Image
- **License**: Check the model repository for license details

## License

This API wrapper is provided as-is. Please check the Qwen-Image model license for usage terms.
