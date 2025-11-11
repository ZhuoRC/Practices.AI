"""
ElevenLabs Text-to-Speech Implementation

This module provides ElevenLabs TTS implementation.
"""

import logging
from typing import List, Dict, Any
import httpx
import asyncio

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat


logger = logging.getLogger(__name__)


class ElevenLabsTTSService(TTSService):
    """ElevenLabs TTS implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
    
    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices from ElevenLabs."""
        if not self.api_key:
            return []
        
        try:
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                voices = []
                
                for voice in data.get("voices", []):
                    voices.append(VoiceInfo(
                        voice_id=voice["voice_id"],
                        name=voice["name"],
                        language=voice.get("language", "en"),
                        gender=voice.get("gender", "Unknown"),
                        description=voice.get("description", ""),
                        is_neural=True  # ElevenLabs uses neural voices
                    ))
                
                return voices
                
        except Exception as e:
            logger.error(f"Failed to get ElevenLabs voices: {e}")
            return []
    
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using ElevenLabs TTS."""
        if not self.api_key:
            raise ValueError("ElevenLabs service not configured")
        
        self.validate_request(request)
        
        try:
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Prepare request data
            data = {
                "text": request.text,
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                },
                "pronunciation_dictionary_locators": [],
                "model_id": "eleven_multilingual_v2"  # Default model
            }
            
            # Map our format to ElevenLabs format
            format_map = {
                AudioFormat.MP3: "mp3",
                AudioFormat.WAV: "pcm",
                AudioFormat.OGG: "ogg_vorbis"
            }
            output_format = format_map.get(request.output_format, "mp3")
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # First, get the voice settings if available
                try:
                    voice_response = await client.get(
                        f"{self.base_url}/voices/{request.voice_id}/settings",
                        headers=headers
                    )
                    if voice_response.status_code == 200:
                        voice_settings = voice_response.json()
                        data["voice_settings"].update(voice_settings)
                except:
                    # Use default settings if voice-specific settings fail
                    pass
                
                # Adjust voice settings based on our parameters
                # Map speed (0.25-4.0) to ElevenLabs stability (0.0-1.0)
                if request.speed != 1.0:
                    # Inverse relationship: higher speed = lower stability
                    data["voice_settings"]["stability"] = max(0.0, 1.0 - (request.speed - 1.0) * 0.3)
                
                # Synthesize speech
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{request.voice_id}?output_format={output_format}",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                audio_data = response.content
                
                # Estimate duration
                word_count = len(request.text.split())
                estimated_duration = (word_count / 150) * 60 / request.speed
                
                return TTSResponse(
                    audio_data=audio_data,
                    duration=estimated_duration,
                    file_size=len(audio_data),
                    format=request.output_format.value,
                    voice_used=request.voice_id,
                    sample_rate=24000,  # ElevenLabs typically uses 24kHz
                    metadata={
                        "provider": "elevenlabs",
                        "model": "eleven_multilingual_v2"
                    }
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"ElevenLabs API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            raise
    
    async def get_voice_preview(self, voice_id: str) -> bytes:
        """Get voice preview audio."""
        if not self.api_key:
            return b""
        
        try:
            headers = {
                "xi-api-key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/voices/{voice_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                voice_data = response.json()
                # Get preview URL if available
                preview_url = voice_data.get("preview_url")
                if preview_url:
                    preview_response = await client.get(preview_url)
                    preview_response.raise_for_status()
                    return preview_response.content
                
                # If no preview URL, generate a short sample
                sample_text = "Hello, this is a preview of my voice."
                request = TTSRequest(
                    text=sample_text,
                    voice_id=voice_id,
                    output_format=AudioFormat.MP3
                )
                response = await self.synthesize(request)
                return response.audio_data
                
        except Exception as e:
            logger.error(f"Failed to get ElevenLabs voice preview: {e}")
            return b""
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get ElevenLabs provider information."""
        return {
            "name": "ElevenLabs",
            "description": "Advanced AI voice synthesis with realistic voices",
            "capabilities": [
                "realistic_voices",
                "voice_cloning",
                "multilingual",
                "emotional_control",
                "custom_voice_design",
                "instant_voice_cloning"
            ],
            "max_text_length": 5000,
            "supported_formats": [AudioFormat.MP3.value, AudioFormat.WAV.value, AudioFormat.OGG.value],
            "is_configured": bool(self.api_key)
        }
