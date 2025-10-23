#!/usr/bin/env python3
"""
Qwen-Image RESTful API Server
Provides text-to-image generation using the Qwen-Image model
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Qwen-Image API",
    description="RESTful API for text-to-image generation using Qwen-Image model",
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
    num_inference_steps: Optional[int] = Field(default=50, description="Number of inference steps", ge=1, le=100)
    true_cfg_scale: Optional[float] = Field(default=4.0, description="Guidance scale", ge=1.0, le=20.0)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    enhance_prompt: Optional[bool] = Field(default=True, description="Add magic prompt enhancement")
    return_base64: Optional[bool] = Field(default=False, description="Return image as base64 string instead of binary")

class ImageGenerationResponse(BaseModel):
    """Response model for image generation"""
    success: bool
    message: str
    image_base64: Optional[str] = None

@app.on_event("startup")
async def load_model():
    """Load the Qwen-Image model on startup"""
    global pipe

    try:
        logger.info("Loading Qwen-Image model...")
        model_name = "Qwen/Qwen-Image"

        # Determine device and dtype
        if torch.cuda.is_available():
            torch_dtype = torch.bfloat16
            device = "cuda"
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            torch_dtype = torch.float32
            device = "cpu"
            logger.info("GPU not available, using CPU")

        # Load the pipeline
        pipe = DiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch_dtype
        )
        pipe = pipe.to(device)

        logger.info("Model loaded successfully!")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen-Image API",
        "status": "running",
        "model": "Qwen/Qwen-Image",
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
                prompt = f"{prompt}, 超清，4K，电影级构图."
            else:
                prompt = f"{prompt}, Ultra HD, 4K, cinematic composition."

        logger.info(f"Generating image with prompt: {prompt}")

        # Prepare generator for seed
        generator = None
        if request.seed is not None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(request.seed)

        # Generate image
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
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
