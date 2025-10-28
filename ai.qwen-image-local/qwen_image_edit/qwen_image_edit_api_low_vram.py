#!/usr/bin/env python3
"""
Qwen-Image-Edit RESTful API Server (Low VRAM Version)
Optimized for GPUs with 6-8GB VRAM
Uses aggressive memory optimizations including sequential CPU offload
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
import gc
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

def cleanup_memory():
    """Aggressive memory cleanup"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        torch.cuda.ipc_collect()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the Qwen-Image-Edit model on startup"""
    global pipe

    try:
        logger.info("=" * 60)
        logger.info("Loading Qwen-Image-Edit-2509 model (LOW VRAM MODE)")
        logger.info("=" * 60)
        model_name = "Qwen/Qwen-Image-Edit-2509"

        # Check GPU
        if torch.cuda.is_available():
            device = "cuda"
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"Total GPU Memory: {gpu_mem:.1f} GB")

            # Use bfloat16 for better numerical stability
            torch_dtype = torch.bfloat16
            logger.info("Using torch.bfloat16 for memory efficiency and numerical stability")
        else:
            torch_dtype = torch.float16
            device = "cpu"
            logger.info("GPU not available, using CPU")

        # Load the pipeline
        logger.info("\nLoading pipeline from pretrained model...")
        logger.info("(This may take several minutes on first run)")

        pipe = QwenImageEditPipeline.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            use_safetensors=True,
        )

        if torch.cuda.is_available():
            logger.info("\n" + "=" * 60)
            logger.info("Applying AGGRESSIVE memory optimizations:")
            logger.info("=" * 60)

            # 1. Enable attention slicing (most aggressive)
            pipe.enable_attention_slicing(slice_size=1)
            logger.info("✓ Enabled attention slicing (slice_size=1)")

            # 2. Enable VAE slicing
            if hasattr(pipe, 'enable_vae_slicing'):
                pipe.enable_vae_slicing()
                logger.info("✓ Enabled VAE slicing")

            # 3. VAE tiling - DISABLED (conflicts with sequential CPU offload)
            logger.info("✓ VAE tiling disabled (incompatible with CPU offload)")

            # 4. Use sequential CPU offload for lowest VRAM usage
            logger.info("✓ Enabling sequential CPU offload...")
            logger.info("  (Components will be moved to GPU only when needed)")
            pipe.enable_sequential_cpu_offload()

            # 5. Try to enable xformers for memory efficient attention
            try:
                pipe.enable_xformers_memory_efficient_attention()
                logger.info("✓ Enabled xformers memory efficient attention")
            except Exception as e:
                logger.warning(f"! Could not enable xformers: {e}")
                logger.info("  (Continuing without xformers)")

            # Clean up
            cleanup_memory()
            logger.info("✓ Initial memory cleanup completed")

        else:
            pipe = pipe.to(device)

        logger.info("\n" + "=" * 60)
        logger.info("Model loaded successfully!")
        logger.info("=" * 60)

        if torch.cuda.is_available():
            logger.info(f"\nCurrent GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
            logger.info(f"Current GPU memory reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")

    except Exception as e:
        logger.error(f"\n❌ Failed to load model: {e}")
        logger.error("\nTroubleshooting tips:")
        logger.error("1. Ensure you have at least 6GB free GPU memory")
        logger.error("2. Close all other GPU applications")
        logger.error("3. Try restarting your system")
        logger.error("4. Consider using CPU mode (slower but more reliable)")
        raise

    # Yield control back to the application
    yield

    # Cleanup on shutdown (if needed)
    logger.info("Shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Qwen-Image-Edit API (Low VRAM)",
    description="RESTful API optimized for GPUs with limited VRAM (6-8GB)",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen-Image-Edit API (Low VRAM Mode)",
        "status": "running",
        "model": "Qwen/Qwen-Image-Edit-2509",
        "mode": "Low VRAM - Sequential CPU Offload",
        "optimizations": [
            "Sequential CPU offload",
            "Aggressive attention slicing",
            "VAE slicing",
            "FP16 precision",
            "Automatic memory cleanup"
        ],
        "recommended_settings": {
            "max_width": 1024,
            "max_height": 1024,
            "recommended_size": "768x768 or smaller",
            "max_steps": 50,
            "recommended_steps": "20-30"
        },
        "endpoints": {
            "/edit": "POST - Edit image with text prompt",
            "/health": "GET - Health check with memory stats",
            "/cleanup": "POST - Force cleanup GPU memory",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with memory statistics"""
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    health_info = {
        "status": "healthy",
        "model_loaded": pipe is not None,
        "device": device,
        "mode": "Sequential CPU Offload" if device == "cuda" else "CPU"
    }

    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3

        health_info.update({
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_total": f"{total:.2f} GB",
            "gpu_memory_allocated": f"{allocated:.2f} GB",
            "gpu_memory_reserved": f"{reserved:.2f} GB",
            "gpu_memory_free": f"{total - reserved:.2f} GB"
        })

    return health_info

@app.post("/cleanup")
async def cleanup():
    """Force aggressive memory cleanup"""
    logger.info("Performing aggressive memory cleanup...")
    cleanup_memory()

    result = {"message": "Memory cleanup completed"}

    if torch.cuda.is_available():
        result["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB"
        result["gpu_memory_reserved"] = f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB"

    return result

@app.post("/edit")
async def edit_image(
    prompt: str = Form(..., description="Text prompt describing desired edits"),
    image: Optional[UploadFile] = File(None, description="Input image file"),
    image_base64: Optional[str] = Form(None, description="Input image as base64 string"),
    negative_prompt: Optional[str] = Form("blurry, distorted, low quality, artifacts", description="Negative prompt"),
    width: Optional[int] = Form(None, description="Output image width (None = keep original)"),
    height: Optional[int] = Form(None, description="Output image height (None = keep original)"),
    num_inference_steps: Optional[int] = Form(30, description="Number of inference steps (reduced default)", ge=10, le=50),
    guidance_scale: Optional[float] = Form(7.5, description="Guidance scale", ge=1.0, le=20.0),
    seed: Optional[int] = Form(None, description="Random seed for reproducibility"),
    return_base64: Optional[bool] = Form(False, description="Return image as base64 string instead of binary")
):
    """
    Edit an image based on a text prompt (LOW VRAM version)

    Optimized for GPUs with 6-8GB VRAM
    """
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Aggressive cleanup before editing
        logger.info("\n" + "=" * 60)
        logger.info("Starting image editing (LOW VRAM MODE)")
        logger.info("=" * 60)
        cleanup_memory()

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
        try:
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

            # Validate image dimensions
            if input_img.size[0] == 0 or input_img.size[1] == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image dimensions: {input_img.size}"
                )

            # Validate image is not too large
            max_dimension = 2048
            if input_img.size[0] > max_dimension or input_img.size[1] > max_dimension:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image too large. Maximum dimension is {max_dimension}px, got {input_img.size}"
                )

            logger.info(f"✓ Image loaded successfully: {input_img.size} ({input_img.mode})")

        except binascii.Error as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {str(e)}")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=400, detail=f"Failed to load image: {str(e)}")

        # Validate and warn about large sizes
        target_width = width if width is not None else input_img.size[0]
        target_height = height if height is not None else input_img.size[1]

        if target_width > 1024 or target_height > 1024:
            logger.warning(f"⚠️  Large image size requested: {target_width}x{target_height}")
            logger.warning("   This may cause OOM errors. Consider using 768x768 or smaller.")

        logger.info(f"Prompt: {prompt}")
        logger.info(f"Input size: {input_img.size}")
        logger.info(f"Output size: {target_width}x{target_height}")
        logger.info(f"Steps: {num_inference_steps}")

        if torch.cuda.is_available():
            mem_before = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory before: {mem_before:.2f} GB")

        # Prepare generator for seed
        generator = None
        if seed is not None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(seed)
            logger.info(f"Seed: {seed}")

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

        # Edit image with inference mode
        logger.info("\nEditing image...")
        with torch.inference_mode():
            result = pipe(**edit_params)

        # Get the edited image
        edited_image = result.images[0]
        logger.info("✓ Image edited successfully!")

        # Save image to local images folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"edited_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        edited_image.save(filepath)
        logger.info(f"Edited image saved to: {filepath}")

        # Aggressive cleanup after editing
        cleanup_memory()

        if torch.cuda.is_available():
            mem_after = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory after: {mem_after:.2f} GB")

        # Convert to base64 or binary
        if return_base64:
            buffered = io.BytesIO()
            edited_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            logger.info("=" * 60 + "\n")
            return ImageEditResponse(
                success=True,
                message="Image edited successfully",
                image_base64=img_str
            )
        else:
            buffered = io.BytesIO()
            edited_image.save(buffered, format="PNG")
            buffered.seek(0)

            logger.info("=" * 60 + "\n")
            return Response(
                content=buffered.getvalue(),
                media_type="image/png",
                headers={
                    "Content-Disposition": "inline; filename=edited_image.png"
                }
            )

    except torch.cuda.OutOfMemoryError as e:
        logger.error("\n" + "=" * 60)
        logger.error("❌ CUDA OUT OF MEMORY ERROR")
        logger.error("=" * 60)
        cleanup_memory()

        suggestions = [
            "Reduce output size to 512x512 or 768x768",
            "Reduce num_inference_steps to 15-20",
            "Close all other GPU applications",
            "Restart the API server to clear memory",
            "Use CPU mode (set CUDA_VISIBLE_DEVICES='' before starting)"
        ]

        logger.error("\n💡 Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            logger.error(f"   {i}. {suggestion}")

        raise HTTPException(
            status_code=507,
            detail={
                "error": "GPU out of memory",
                "message": "The requested image editing exceeded available GPU memory",
                "suggestions": suggestions,
                "your_request": {
                    "width": width,
                    "height": height,
                    "steps": num_inference_steps
                },
                "try_instead": {
                    "width": 512,
                    "height": 512,
                    "steps": 20
                }
            }
        )
    except Exception as e:
        logger.error(f"\n❌ Error editing image: {e}")
        cleanup_memory()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("Starting Qwen-Image-Edit API Server (LOW VRAM MODE)")
    logger.info("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8021,
        log_level="info"
    )
