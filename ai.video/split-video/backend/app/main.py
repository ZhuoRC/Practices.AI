from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

try:
    from .api import video
    from .config import settings
except ImportError:
    from app.api import video
    from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    print("=" * 60)
    print("AI Video Splitter API Starting...")
    print("=" * 60)
    print(f"Whisper Model: {settings.whisper_model}")
    print(f"LLM Provider: {settings.llm_provider.upper()}")
    if settings.llm_provider == "qwen":
        print(f"  Qwen API Base: {settings.qwen_api_base}")
        print(f"  Qwen Model: {settings.qwen_model}")
    else:
        print(f"  Ollama URL: {settings.ollama_base_url}")
        print(f"  Ollama Model: {settings.ollama_model}")
    print(f"Target Chapter Duration: {settings.target_chapter_duration // 60} minutes")
    print(f"Upload Path: {settings.upload_path}")
    print(f"Processed Path: {settings.processed_path}")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("AI Video Splitter API Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AI Video Splitter API",
    description="""
## AI-Powered Video Splitting System

This API provides intelligent video splitting using Whisper for subtitle extraction and LLM for semantic chapter segmentation.

### Features
- **Video Upload**: Support for common video formats (MP4, AVI, MOV, MKV)
- **Subtitle Extraction**: Automatic subtitle generation with Whisper (word-level timestamps)
- **Intelligent Segmentation**: LLM-based chapter splitting (~10 minutes each)
- **Video Processing**: Automatic video splitting into chapters using ffmpeg
- **Tree View**: Parent-child relationship between original and split videos
- **Preview**: Video and subtitle preview for all segments

### Workflow
1. **Upload**: Upload video file via `/api/video/upload`
2. **Process**: System automatically:
   - Extracts subtitles with Whisper
   - Analyzes content with LLM to create chapters
   - Splits video into chapter segments
3. **Monitor**: Check progress at `/api/video/status/{task_id}`
4. **View**: Get tree structure at `/api/video/tree/{video_id}`
5. **Preview**: Stream videos and subtitles for preview

### Getting Started
1. Upload a video at `/api/video/upload`
2. Monitor processing status with the returned `task_id`
3. Once complete, view the video tree structure
4. Preview individual chapters and subtitles
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "video",
            "description": "Video upload, processing, and preview operations",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Video Splitter API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/video/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
