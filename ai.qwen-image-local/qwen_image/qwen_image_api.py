#!/usr/bin/env python3
"""
Z-Image RESTful API Server
Provides text-to-image generation using the Z-Image model
Reference: https://github.com/Tongyi-MAI/Z-Image
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from contextlib import asynccontextmanager
import torch
from diffusers import DiffusionPipeline
import io
import base64
from PIL import Image
import uvicorn
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if CPU mode is forced
USE_CPU = os.environ.get("USE_CPU", "false").lower() in ("true", "1", "yes")

# Create output directory
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(IMAGES_DIR, exist_ok=True)
logger.info(f"Images will be saved to: {IMAGES_DIR}")

# Global variable to store the pipeline
pipe = None

class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text prompt to generate image from")
    negative_prompt: Optional[str] = Field(default=" ", description="Negative prompt")
    width: Optional[int] = Field(default=768, description="Image width", ge=256, le=2048)
    height: Optional[int] = Field(default=768, description="Image height", ge=256, le=2048)
    num_inference_steps: Optional[int] = Field(default=30, description="Number of inference steps", ge=1, le=100)
    guidance_scale: Optional[float] = Field(default=4.0, description="Guidance scale", ge=1.0, le=20.0)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    enhance_prompt: Optional[bool] = Field(default=True, description="Add magic prompt enhancement")
    return_base64: Optional[bool] = Field(default=False, description="Return image as base64 string instead of binary")

class ImageGenerationResponse(BaseModel):
    """Response model for image generation"""
    success: bool
    message: str
    image_base64: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the Z-Image model on startup"""
    global pipe

    try:
        logger.info("Loading Z-Image model...")
        model_name = "Tongyi-MAI/Z-Image"

        # Determine device and dtype
        if USE_CPU:
            torch_dtype = torch.float32
            device = "cpu"
            logger.info("CPU mode forced by environment variable")
        elif torch.cuda.is_available():
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU Memory: {gpu_memory_gb:.1f} GB")
            
            # Z-Image can run with 4GB+ GPU memory (float16 precision)
            if gpu_memory_gb < 4:
                logger.warning(f"GPU memory ({gpu_memory_gb:.1f} GB) is insufficient for Z-Image model")
                logger.info("Switching to CPU mode (slower but will work)")
                torch_dtype = torch.float32
                device = "cpu"
            else:
                torch_dtype = torch.float16  # Z-Image uses float16
                device = "cuda"
                logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"GPU mode enabled with float16 precision")
        else:
            torch_dtype = torch.float32
            device = "cpu"
            logger.info("GPU not available, using CPU")

        # Load pipeline
        logger.info(f"Loading model from {model_name}...")
        pipe = DiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch_dtype
        )
        
        if device == "cpu":
            logger.info("Loading model to CPU (this will take several minutes)...")
        
        pipe = pipe.to(device)

        logger.info("Model loaded successfully!")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

    # Yield control back to the application
    yield

    # Cleanup on shutdown (if needed)
    logger.info("Shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Z-Image API",
    description="RESTful API for text-to-image generation using Z-Image model",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Z-Image API",
        "status": "running",
        "model": "Tongyi-MAI/Z-Image",
        "endpoints": {
            "/generate": "POST - Generate image from text prompt",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "status": "healthy",
        "model_loaded": pipe is not None,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Generate an image from a text prompt

    Returns the generated image as binary data (PNG) by default,
    or as base64 string if return_base64=True
    """
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Enhance prompt if requested
        prompt = request.prompt
        if request.enhance_prompt:
            # Check if prompt is in Chinese or English
            if any('\u4e00' <= char <= '\u9fff' for char in prompt):
                prompt = f"{prompt}"
            else:
                prompt = f"{prompt}"

        logger.info(f"Generating image with prompt: {prompt}")
        logger.info(f"Parameters: {request.width}x{request.height}, {request.num_inference_steps} steps, guidance={request.guidance_scale}")

        # Prepare generator for seed
        generator = None
        if request.seed is not None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(request.seed)

        # Generate image with progress callback
        logger.info("Starting image generation (this may take 30-60 seconds for first time)...")
        result = pipe(
            prompt=prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            generator=generator
        )
        logger.info("Image generation completed!")

        # Get the generated image
        image = result.images[0]

        # Save image to local images folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath)
        logger.info(f"Image saved to: {filepath}")

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

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8501,
        log_level="info"
    )