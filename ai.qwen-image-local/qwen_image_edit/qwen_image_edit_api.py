#!/usr/bin/env python3
"""
Qwen-Image-Edit RESTful API Server
Provides image editing capabilities using the Qwen-Image-Edit-2509 model
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional
from contextlib import asynccontextmanager
import torch
from diffusers import QwenImageEditPipeline
import io
import base64
import binascii
from PIL import Image
import uvicorn
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create output directory
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(IMAGES_DIR, exist_ok=True)
logger.info(f"Edited images will be saved to: {IMAGES_DIR}")

# Global variable to store the pipeline
pipe = None

class ImageEditResponse(BaseModel):
    """Response model for image editing"""
    success: bool
    message: str
    image_base64: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the Qwen-Image-Edit model on startup"""
    global pipe

    try:
        logger.info("Loading Qwen-Image-Edit-2509 model...")
        model_name = "Qwen/Qwen-Image-Edit-2509"

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
        pipe = QwenImageEditPipeline.from_pretrained(
            model_name,
            torch_dtype=torch_dtype
        )
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
    title="Qwen-Image-Edit API",
    description="RESTful API for image editing using Qwen-Image-Edit-2509 model",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen-Image-Edit API",
        "status": "running",
        "model": "Qwen/Qwen-Image-Edit-2509",
        "endpoints": {
            "/edit": "POST - Edit image with text prompt",
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

@app.post("/edit", response_model=ImageEditResponse)
async def edit_image(
    prompt: str = Form(..., description="Text prompt describing desired edits"),
    image: Optional[UploadFile] = File(None, description="Input image file"),
    image_base64: Optional[str] = Form(None, description="Input image as base64 string"),
    negative_prompt: Optional[str] = Form("blurry, distorted, low quality, artifacts", description="Negative prompt"),
    width: Optional[int] = Form(None, description="Output image width (None = keep original)"),
    height: Optional[int] = Form(None, description="Output image height (None = keep original)"),
    num_inference_steps: Optional[int] = Form(50, description="Number of inference steps", ge=1, le=100),
    guidance_scale: Optional[float] = Form(7.5, description="Guidance scale", ge=1.0, le=20.0),
    seed: Optional[int] = Form(None, description="Random seed for reproducibility"),
    return_base64: Optional[bool] = Form(False, description="Return image as base64 string instead of binary")
):
    """
    Edit an image based on a text prompt

    Accepts image as multipart file upload OR base64 string
    Returns the edited image as binary data (PNG) by default,
    or as base64 string if return_base64=True
    """
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Normalize empty strings to None for proper validation
        if image_base64 is not None and image_base64.strip() == "":
            image_base64 = None

        # Validate that exactly one image input is provided
        if image is not None and image_base64 is not None:
            raise HTTPException(
                status_code=400,
                detail="Cannot provide both 'image' and 'image_base64'. Please provide only one."
            )

        if image is None and image_base64 is None:
            raise HTTPException(
                status_code=400,
                detail="Either 'image' file or 'image_base64' must be provided"
            )

        # Load input image
        input_img = None
        if image is not None:
            # Load from uploaded file
            logger.info("Loading image from uploaded file...")
            img_bytes = await image.read()
            if len(img_bytes) == 0:
                raise HTTPException(status_code=400, detail="Uploaded image file is empty")
            input_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        else:  # image_base64 is not None
            # Load from base64 string
            logger.info("Loading image from base64 string...")
            img_data = base64.b64decode(image_base64)
            if len(img_data) == 0:
                raise HTTPException(status_code=400, detail="Base64 image data is empty")
            input_img = Image.open(io.BytesIO(img_data)).convert("RGB")

        # Validate that image was successfully loaded
        if input_img is None:
            raise HTTPException(status_code=500, detail="Failed to load image")

        logger.info(f"✓ Image loaded successfully: {input_img.size}")

        logger.info(f"Editing image with prompt: {prompt}")
        logger.info(f"Input image size: {input_img.size}")

        # Prepare generator for seed
        generator = None
        if seed is not None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(seed)

        # Prepare editing parameters
        edit_params = {
            "prompt": prompt,
            "image": input_img,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "generator": generator
        }

        # Add width/height if specified
        if width is not None:
            edit_params["width"] = width
        if height is not None:
            edit_params["height"] = height

        # Edit image
        result = pipe(**edit_params)

        # Get the edited image
        edited_image = result.images[0]

        # Save image to local images folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"edited_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        edited_image.save(filepath)
        logger.info(f"Edited image saved to: {filepath}")

        # Convert to base64 or binary
        if return_base64:
            # Convert to base64
            buffered = io.BytesIO()
            edited_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return ImageEditResponse(
                success=True,
                message="Image edited successfully",
                image_base64=img_str
            )
        else:
            # Return binary image data
            buffered = io.BytesIO()
            edited_image.save(buffered, format="PNG")
            buffered.seek(0)

            return Response(
                content=buffered.getvalue(),
                media_type="image/png",
                headers={
                    "Content-Disposition": "inline; filename=edited_image.png"
                }
            )

    except binascii.Error as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {str(e)}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Error editing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8020,
        log_level="info"
    )
