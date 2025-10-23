#!/usr/bin/env python3
"""
Qwen-Image RESTful API Server (Low VRAM Version)
Optimized for GPUs with 6-8GB VRAM
Uses aggressive memory optimizations including sequential CPU offload
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Qwen-Image API (Low VRAM)",
    description="RESTful API optimized for GPUs with limited VRAM (6-8GB)",
    version="1.0.0"
)

# Global variable to store the pipeline
pipe = None

class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text prompt to generate image from")
    negative_prompt: Optional[str] = Field(default=" ", description="Negative prompt")
    width: Optional[int] = Field(default=768, description="Image width (reduced default)", ge=256, le=1024)
    height: Optional[int] = Field(default=768, description="Image height (reduced default)", ge=256, le=1024)
    num_inference_steps: Optional[int] = Field(default=25, description="Number of inference steps (reduced)", ge=10, le=50)
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
    """Aggressive memory cleanup"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        torch.cuda.ipc_collect()

@app.on_event("startup")
async def load_model():
    """Load the Qwen-Image model with aggressive memory optimizations"""
    global pipe

    try:
        logger.info("=" * 60)
        logger.info("Loading Qwen-Image model (LOW VRAM MODE)")
        logger.info("=" * 60)
        model_name = "Qwen/Qwen-Image"

        # Check GPU
        if torch.cuda.is_available():
            device = "cuda"
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"Total GPU Memory: {gpu_mem:.1f} GB")

            # Force float16 for memory efficiency
            torch_dtype = torch.float16
            logger.info("Using torch.float16 for maximum memory efficiency")
        else:
            torch_dtype = torch.float32
            device = "cpu"
            logger.info("GPU not available, using CPU")

        # Load the pipeline
        logger.info("\nLoading pipeline from pretrained model...")
        logger.info("(This may take several minutes on first run)")
        
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.autocast("cuda", enabled=False)

        pipe = DiffusionPipeline.from_pretrained(
            model_name,
            # torch_dtype=torch_dtype,
            dtype=torch.float16,
            use_safetensors=True
            # device_map="auto",
            # use_xformers=False      
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

            # 3. Enable VAE tiling
            if hasattr(pipe, 'enable_vae_tiling'):
                pipe.enable_vae_tiling()
                logger.info("✓ Enabled VAE tiling")

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

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen-Image API (Low VRAM Mode)",
        "status": "running",
        "model": "Qwen/Qwen-Image",
        "mode": "Low VRAM - Sequential CPU Offload",
        "optimizations": [
            "Sequential CPU offload",
            "Aggressive attention slicing",
            "VAE slicing and tiling",
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
            "/generate": "POST - Generate image from text prompt",
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

@app.post("/generate")
async def generate_image(request: ImageGenerationRequest):
    """
    Generate an image from a text prompt (LOW VRAM version)

    Optimized for GPUs with 6-8GB VRAM
    """
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Aggressive cleanup before generation
        logger.info("\n" + "=" * 60)
        logger.info("Starting image generation (LOW VRAM MODE)")
        logger.info("=" * 60)
        cleanup_memory()

        # Validate and warn about large sizes
        if request.width > 1024 or request.height > 1024:
            logger.warning(f"⚠️  Large image size requested: {request.width}x{request.height}")
            logger.warning("   This may cause OOM errors. Consider using 768x768 or smaller.")

        # Enhance prompt if requested
        prompt = request.prompt
        if request.enhance_prompt:
            if any('\u4e00' <= char <= '\u9fff' for char in prompt):
                prompt = f"{prompt}, 电影级构图."
            else:
                prompt = f"{prompt}, cinematic composition."

        logger.info(f"Prompt: {prompt}")
        logger.info(f"Size: {request.width}x{request.height}")
        logger.info(f"Steps: {request.num_inference_steps}")

        if torch.cuda.is_available():
            mem_before = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory before: {mem_before:.2f} GB")

        # Prepare generator for seed
        generator = None
        if request.seed is not None:
            # Generator should be on CPU for sequential offload
            generator = torch.Generator(device="cpu").manual_seed(request.seed)
            logger.info(f"Seed: {request.seed}")

        # Generate image with inference mode
        logger.info("\nGenerating image...")
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
        logger.info("✓ Image generated successfully!")

        # Aggressive cleanup after generation
        cleanup_memory()

        if torch.cuda.is_available():
            mem_after = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory after: {mem_after:.2f} GB")

        # Convert to base64 or binary
        if request.return_base64:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            logger.info("=" * 60 + "\n")
            return ImageGenerationResponse(
                success=True,
                message="Image generated successfully",
                image_base64=img_str
            )
        else:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            logger.info("=" * 60 + "\n")
            return Response(
                content=buffered.getvalue(),
                media_type="image/png",
                headers={
                    "Content-Disposition": "inline; filename=generated_image.png"
                }
            )

    except torch.cuda.OutOfMemoryError as e:
        logger.error("\n" + "=" * 60)
        logger.error("❌ CUDA OUT OF MEMORY ERROR")
        logger.error("=" * 60)
        cleanup_memory()

        suggestions = [
            "Reduce image size to 512x512 or 768x768",
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
                "message": "The requested image generation exceeded available GPU memory",
                "suggestions": suggestions,
                "your_request": {
                    "width": request.width,
                    "height": request.height,
                    "steps": request.num_inference_steps
                },
                "try_instead": {
                    "width": 512,
                    "height": 512,
                    "steps": 20
                }
            }
        )
    except Exception as e:
        logger.error(f"\n❌ Error generating image: {e}")
        cleanup_memory()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("Starting Qwen-Image API Server (LOW VRAM MODE)")
    logger.info("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
