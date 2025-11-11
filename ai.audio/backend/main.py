"""
AI Audio TTS Service

FastAPI application for text-to-speech generation using multiple TTS providers.
"""

import os
import sys
import logging
import time
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from io import BytesIO
import base64

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
import aiofiles

from tts_services.base import (
    TTSService, 
    TTSRequest as CoreTTSRequest, 
    TTSResponse as CoreTTSResponse,
    VoiceInfo,
    AudioFormat
)
from tts_services import (
    AzureTTSService,
    GoogleTTSService,
    ElevenLabsTTSService,
    LocalTTSService,
    WindowsSimpleTTSService,
    XTTSV2TTSService
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="AI Audio TTS Service",
    description="Text-to-Speech API with multiple provider support",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Incoming Request: {request.method} {request.url}")
    logger.info(f"Client IP: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Log response details
    process_time = time.time() - start_time
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Processing Time: {process_time:.2f}s")
    logger.info("=" * 80)
    
    return response

# Pydantic models for API
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    provider: str = Field(..., description="TTS provider (azure, google, elevenlabs, local)")
    voice_id: str = Field(..., description="Voice ID to use")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed (0.25-4.0)")
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0, description="Pitch adjustment (-20 to +20 Hz)")
    volume: float = Field(default=1.0, ge=0.0, le=2.0, description="Volume level (0.0-2.0)")
    output_format: AudioFormat = Field(default=AudioFormat.MP3, description="Audio output format")
    sample_rate: Optional[int] = Field(default=None, description="Sample rate override")

class TTSResponse(BaseModel):
    audio_id: str
    duration: float
    file_size: int
    format: str
    provider_used: str
    voice_used: str
    sample_rate: int
    metadata: Optional[Dict[str, Any]] = None
    download_url: str

class ProviderInfo(BaseModel):
    name: str
    description: str
    capabilities: List[str]
    max_text_length: int
    supported_formats: List[str]
    is_configured: bool

class TTSManager:
    """Manages multiple TTS services."""
    
    def __init__(self):
        self.services: Dict[str, TTSService] = {}
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./generated_audio"))
        self.output_dir.mkdir(exist_ok=True)
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all available TTS services."""
        config = {
            "AZURE_SPEECH_KEY": os.getenv("AZURE_SPEECH_KEY"),
            "AZURE_SPEECH_REGION": os.getenv("AZURE_SPEECH_REGION", "eastus"),
            "GOOGLE_TTS_KEY": os.getenv("GOOGLE_TTS_KEY"),
            "GOOGLE_TTS_PROJECT_ID": os.getenv("GOOGLE_TTS_PROJECT_ID"),
            "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
            "LOCAL_TTS_MODEL_PATH": os.getenv("LOCAL_TTS_MODEL_PATH", "./models"),
            "LOCAL_TTS_DEFAULT_VOICE": os.getenv("LOCAL_TTS_DEFAULT_VOICE", "en-us-lessac-medium"),
            "XTTS_V2_DEFAULT_SPEAKER": os.getenv("XTTS_V2_DEFAULT_SPEAKER", "default"),
            "XTTS_V2_DEFAULT_LANGUAGE": os.getenv("XTTS_V2_DEFAULT_LANGUAGE", "en"),
            "XTTS_V2_MODEL_PATH": os.getenv("XTTS_V2_MODEL_PATH", None),
            "XTTS_V2_USE_GPU": os.getenv("XTTS_V2_USE_GPU", "false").lower() == "true",
            "XTTS_V2_VOICE_SAMPLES_PATH": os.getenv("XTTS_V2_VOICE_SAMPLES_PATH", "./voice_samples")
        }
        
        # Initialize services
        self.services["azure"] = AzureTTSService(config)
        self.services["google"] = GoogleTTSService(config)
        self.services["elevenlabs"] = ElevenLabsTTSService(config)
        self.services["local"] = LocalTTSService(config)
        self.services["windows"] = WindowsSimpleTTSService(config)
        self.services["xtts_v2"] = XTTSV2TTSService(config)
        
        logger.info("Initialized TTS services:")
        for provider, service in self.services.items():
            info = service.get_provider_info()
            status = "OK" if info["is_configured"] else "FAIL"
            logger.info(f"  {provider}: {info['name']} {status}")
    
    async def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        providers = []
        for provider, service in self.services.items():
            if await service.health_check():
                providers.append(provider)
        return providers
    
    async def get_provider_voices(self, provider: str) -> List[VoiceInfo]:
        """Get available voices for a provider."""
        if provider not in self.services:
            raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
        
        try:
            voices = await self.services[provider].get_available_voices()
            return voices
        except Exception as e:
            logger.error(f"Failed to get voices for {provider}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")
    
    async def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech and save to file."""
        if request.provider not in self.services:
            raise HTTPException(status_code=404, detail=f"Provider '{request.provider}' not found")
        
        service = self.services[request.provider]
        
        # Check if service is healthy
        if not await service.health_check():
            raise HTTPException(status_code=503, detail=f"Provider '{request.provider}' is not available")
        
        try:
            # Convert API request to core request
            core_request = CoreTTSRequest(
                text=request.text,
                voice_id=request.voice_id,
                speed=request.speed,
                pitch=request.pitch,
                volume=request.volume,
                output_format=request.output_format,
                sample_rate=request.sample_rate
            )
            
            # Synthesize speech
            logger.info(f"Synthesizing speech with {request.provider} using voice {request.voice_id}")
            start_time = time.time()
            
            response: CoreTTSResponse = await service.synthesize(core_request)
            
            synthesis_time = time.time() - start_time
            logger.info(f"Speech synthesis completed in {synthesis_time:.2f}s")
            
            # Generate unique audio ID
            audio_id = str(uuid.uuid4())
            
            # Save audio file
            file_extension = request.output_format.value
            filename = f"{audio_id}.{file_extension}"
            filepath = self.output_dir / filename
            
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(response.audio_data)
            
            # Prepare response
            api_response = TTSResponse(
                audio_id=audio_id,
                duration=response.duration,
                file_size=response.file_size,
                format=response.format,
                provider_used=request.provider,
                voice_used=response.voice_used,
                sample_rate=response.sample_rate,
                metadata=response.metadata,
                download_url=f"/audio/{audio_id}"
            )
            
            logger.info(f"Audio saved as {filename} ({response.file_size} bytes)")
            return api_response
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")
    
    async def get_audio_file(self, audio_id: str) -> Optional[Path]:
        """Get audio file path by ID."""
        # Try different extensions
        for ext in ['mp3', 'wav', 'ogg', 'flac']:
            filepath = self.output_dir / f"{audio_id}.{ext}"
            if filepath.exists():
                return filepath
        return None
    
    async def get_provider_info(self, provider: str) -> ProviderInfo:
        """Get provider information."""
        if provider not in self.services:
            raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
        
        service = self.services[provider]
        info = service.get_provider_info()
        
        return ProviderInfo(**info)

# Initialize TTS Manager
tts_manager = TTSManager()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Audio TTS Service is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    providers = await tts_manager.get_available_providers()
    return {
        "status": "healthy",
        "available_providers": providers,
        "total_providers": len(tts_manager.services)
    }

@app.get("/providers", response_model=List[str])
async def get_providers():
    """Get available TTS providers."""
    return await tts_manager.get_available_providers()

@app.get("/providers/{provider}/info", response_model=ProviderInfo)
async def get_provider_info(provider: str):
    """Get provider information."""
    return await tts_manager.get_provider_info(provider)

@app.get("/providers/{provider}/voices")
async def get_voices(provider: str):
    """Get available voices for a provider."""
    voices = await tts_manager.get_provider_voices(provider)
    return {
        "provider": provider,
        "voices": [voice.dict() for voice in voices]
    }

@app.post("/generate", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """Generate speech from text."""
    return await tts_manager.synthesize_speech(request)

@app.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """Download generated audio file."""
    filepath = await tts_manager.get_audio_file(audio_id)
    if not filepath:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Determine media type
    ext = filepath.suffix.lower()
    media_types = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac'
    }
    media_type = media_types.get(ext, 'application/octet-stream')
    
    async def audio_stream():
        async with aiofiles.open(filepath, 'rb') as f:
            while chunk := await f.read(8192):
                yield chunk
    
    return StreamingResponse(
        audio_stream(),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filepath.name}"
        }
    )

@app.get("/voices/{provider}/{voice_id}/preview")
async def get_voice_preview(provider: str, voice_id: str):
    """Get voice preview audio."""
    if provider not in tts_manager.services:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
    
    try:
        service = tts_manager.services[provider]
        preview_data = await service.get_voice_preview(voice_id)
        
        if not preview_data:
            raise HTTPException(status_code=404, detail="Voice preview not available")
        
        return Response(
            content=preview_data,
            media_type="audio/mpeg"
        )
    except Exception as e:
        logger.error(f"Failed to get voice preview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice preview: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7000"))
    
    logger.info(f"Starting AI Audio TTS Service on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        timeout_keep_alive=600,
        timeout_graceful_shutdown=30
    )
