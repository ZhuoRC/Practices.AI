from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers import faceswap
from app.utils.storage import ensure_directories, OUTPUTS_DIR, UPLOADS_DIR

# Create FastAPI app
app = FastAPI(
    title="FaceFusion Video Face Swap API",
    description="API for video face swapping using FaceFusion",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
ensure_directories()

# Mount static files for outputs
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Include routers
app.include_router(faceswap.router)


@app.get("/")
async def root():
    return {
        "message": "FaceFusion Video Face Swap API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
