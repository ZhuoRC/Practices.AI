"""
Base TTS Service Interface

This module defines the base interface and data models for all TTS services.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class AudioFormat(str, Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"


class VoiceInfo(BaseModel):
    """Voice information model."""
    voice_id: str
    name: str
    language: str
    gender: Optional[str] = None
    description: Optional[str] = None
    sample_rate: Optional[int] = None
    is_neural: bool = False


class TTSRequest(BaseModel):
    """TTS generation request model."""
    text: str
    voice_id: str
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    output_format: AudioFormat = AudioFormat.MP3
    sample_rate: Optional[int] = None


class TTSResponse(BaseModel):
    """TTS generation response model."""
    audio_data: bytes
    duration: float
    file_size: int
    format: str
    voice_used: str
    sample_rate: int
    metadata: Optional[Dict[str, Any]] = None


class TTSService(ABC):
    """Base class for all TTS services."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get list of available voices for this TTS service."""
        pass
    
    @abstractmethod
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech from text."""
        pass
    
    @abstractmethod
    async def get_voice_preview(self, voice_id: str) -> bytes:
        """Get preview audio for a voice."""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information and capabilities."""
        pass
    
    def validate_request(self, request: TTSRequest) -> None:
        """Validate TTS request parameters."""
        if not request.text or len(request.text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if request.speed < 0.25 or request.speed > 4.0:
            raise ValueError("Speed must be between 0.25 and 4.0")
        
        if request.volume < 0.0 or request.volume > 2.0:
            raise ValueError("Volume must be between 0.0 and 2.0")
        
        if request.pitch < -20.0 or request.pitch > 20.0:
            raise ValueError("Pitch must be between -20.0 and 20.0")
    
    async def health_check(self) -> bool:
        """Check if the TTS service is healthy and accessible."""
        try:
            voices = await self.get_available_voices()
            return len(voices) > 0
        except Exception:
            return False
