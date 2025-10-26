#!/usr/bin/env python3
"""
Qwen-Image RESTful API Server (Memory Optimized)
Optimized for GPUs with limited VRAM (6-12GB)
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional
import torch
from diffusers import DiffusionPipeline
import io
import base64
from PIL import Image
import uvicorn
import logging
import gc
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create images directory if it doesn't exist
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)
logger.info(f"Images will be saved to: {IMAGES_DIR}")

# Initialize FastAPI app
app = FastAPI(
    title="Qwen-Image API (Memory Optimized)",
    description="RESTful API for text-to-image generation using Qwen-Image model with memory optimizations",
    version="1.0.0"
)

# Global variable to store the pipeline
pipe = None

class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text prompt to generate image from")
    negative_prompt: Optional[str] = Field(default=" ", description="Negative prompt")
    width: Optional[int] = Field(default=1024, description="Image width", ge=256, le=2048)
    height: Optional[int] = Field(default=1024, description="Image height", ge=256, le=2048)
    num_inference_steps: Optional[int] = Field(default=30, description="Number of inference steps (reduced for memory)", ge=1, le=100)
    true_cfg_scale: Optional[float] = Field(default=4.0, description="Guidance scale", ge=1.0, le=20.0)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    enhance_prompt: Optional[bool] = Field(default=True, description="Add magic prompt enhancement")
    return_base64: Optional[bool] = Field(default=False, description="Return image as base64 string instead of binary")

class ImageGenerationResponse(BaseModel):
    """Response model for image generation"""
    success: bool
    message: str
    image_base64: Optional[str] = None

def cleanup_memory():
    """Force garbage collection and clear CUDA cache"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

@app.on_event("startup")
async def load_model():
    """Load the Qwen-Image model on startup with memory optimizations"""
    global pipe

    try:
        logger.info("Loading Qwen-Image model with memory optimizations...")
        model_name = "Qwen/Qwen-Image"

        # Determine device and dtype
        if torch.cuda.is_available():
            device = "cuda"
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {gpu_mem:.1f} GB")

            # Use float16 for better memory efficiency
            torch_dtype = torch.float16
            logger.info("Using torch.float16 for reduced memory usage")
        else:
            torch_dtype = torch.float32
            device = "cpu"
            logger.info("GPU not available, using CPU")

        # Load the pipeline with memory optimizations
        logger.info("Loading pipeline...")
        pipe = DiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            use_safetensors=True
        )

        # Apply memory optimizations
        if torch.cuda.is_available():
            logger.info("Applying memory optimizations...")

            # Enable attention slicing to reduce memory usage
            pipe.enable_attention_slicing(slice_size=1)
            logger.info("✓ Enabled attention slicing")

            # Enable VAE slicing for large images
            if hasattr(pipe, 'enable_vae_slicing'):
                pipe.enable_vae_slicing()
                logger.info("✓ Enabled VAE slicing")

            # Enable VAE tiling for very large images
            if hasattr(pipe, 'enable_vae_tiling'):
                pipe.enable_vae_tiling()
                logger.info("✓ Enabled VAE tiling")

            # Enable CPU offload if memory is very limited (<12GB)
            if gpu_mem < 12:
                logger.info("GPU memory < 12GB, enabling CPU offload...")
                pipe.enable_model_cpu_offload()
                logger.info("✓ Enabled model CPU offload")
            else:
                pipe = pipe.to(device)
                logger.info(f"✓ Moved pipeline to {device}")

            # Enable memory efficient attention if available
            try:
                pipe.enable_xformers_memory_efficient_attention()
                logger.info("✓ Enabled xformers memory efficient attention")
            except Exception as e:
                logger.warning(f"Could not enable xformers: {e}")
                logger.info("  (This is optional, continuing without it)")
        else:
            pipe = pipe.to(device)

        logger.info("Model loaded successfully with optimizations!")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen-Image API (Memory Optimized)",
        "status": "running",
        "model": "Qwen/Qwen-Image",
        "optimizations": [
            "attention slicing",
            "VAE slicing/tiling",
            "CPU offload (if needed)",
            "float16 precision"
        ],
        "endpoints": {
            "/generate": "POST - Generate image from text prompt",
            "/health": "GET - Health check",
            "/cleanup": "POST - Force cleanup GPU memory",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    health_info = {
        "status": "healthy",
        "model_loaded": pipe is not None,
        "device": device
    }

    if torch.cuda.is_available():
        health_info["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB"
        health_info["gpu_memory_reserved"] = f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB"

    return health_info

@app.post("/cleanup")
async def cleanup():
    """Force cleanup GPU memory"""
    cleanup_memory()
    return {"message": "Memory cleanup completed"}

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Generate an image from a text prompt (memory optimized version)

    Returns the generated image as binary data (PNG) by default,
    or as base64 string if return_base64=True
    """
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Clean up before generation
        cleanup_memory()

        # Enhance prompt if requested
        prompt = request.prompt
        if request.enhance_prompt:
            # Check if prompt is in Chinese or English
            if any('\u4e00' <= char <= '\u9fff' for char in prompt):
                prompt = f"{prompt}, 超清，4K，电影级构图."
            else:
                prompt = f"{prompt}, Ultra HD, 4K, cinematic composition."

        logger.info(f"Generating image with prompt: {prompt}")
        logger.info(f"Parameters: {request.width}x{request.height}, steps={request.num_inference_steps}")

        if torch.cuda.is_available():
            logger.info(f"GPU memory before generation: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

        # Prepare generator for seed
        generator = None
        if request.seed is not None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(request.seed)

        # Generate image
        with torch.inference_mode():
            result = pipe(
                prompt=prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
                true_cfg_scale=request.true_cfg_scale,
                generator=generator
            )

        # Get the generated image
        image = result.images[0]

        # Save image to local images folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath)
        logger.info(f"Image saved to: {filepath}")

        # Clean up after generation
        cleanup_memory()

        if torch.cuda.is_available():
            logger.info(f"GPU memory after generation: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

        # Convert to base64 or binary
        if request.return_base64:
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return ImageGenerationResponse(
                success=True,
                message="Image generated successfully",
                image_base64=img_str
            )
        else:
            # Return binary image data
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            return Response(
                content=buffered.getvalue(),
                media_type="image/png",
                headers={
                    "Content-Disposition": "inline; filename=generated_image.png"
                }
            )

    except torch.cuda.OutOfMemoryError as e:
        logger.error(f"CUDA Out of Memory Error: {e}")
        cleanup_memory()

        # Provide helpful error message
        suggestions = [
            "Try reducing image dimensions (e.g., 768x768 or 512x512)",
            "Reduce num_inference_steps (try 20-30)",
            "Close other GPU-intensive applications",
            "Use CPU mode instead (slower but won't run out of memory)"
        ]

        raise HTTPException(
            status_code=507,
            detail={
                "error": "GPU out of memory",
                "message": str(e),
                "suggestions": suggestions
            }
        )
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        cleanup_memory()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
