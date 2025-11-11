"""
Google Cloud Text-to-Speech Implementation

This module provides Google Cloud TTS implementation.
"""

import logging
from typing import List, Dict, Any
from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPICallError
import asyncio

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat


logger = logging.getLogger(__name__)


class GoogleTTSService(TTSService):
    """Google Cloud TTS implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("GOOGLE_TTS_KEY")
        self.project_id = config.get("GOOGLE_TTS_PROJECT_ID")
        
        try:
            self.client = texttospeech.TextToSpeechClient() if self.api_key else None
        except Exception as e:
            logger.warning(f"Failed to initialize Google TTS client: {e}")
            self.client = None
    
    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices from Google Cloud TTS."""
        if not self.client:
            return []
        
        try:
            # Run in thread pool since Google client is synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.list_voices()
            )
            
            voices = []
            for voice in response.voices:
                # Get primary language
                language_codes = voice.language_codes
                primary_lang = language_codes[0] if language_codes else "unknown"
                
                # Get gender
                ssml_gender = voice.ssml_gender
                gender_map = {
                    texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED: "Unknown",
                    texttospeech.SsmlVoiceGender.MALE: "Male",
                    texttospeech.SsmlVoiceGender.FEMALE: "Female",
                    texttospeech.SsmlVoiceGender.NEUTRAL: "Neutral"
                }
                gender = gender_map.get(ssml_gender, "Unknown")
                
                # Check if it's a neural voice (WaveNet)
                is_neural = "WaveNet" in voice.name
                
                voices.append(VoiceInfo(
                    voice_id=voice.name,
                    name=voice.name.split('/')[-1],  # Get just the voice name
                    language=primary_lang,
                    gender=gender,
                    description=f"Google {voice.name}",
                    sample_rate=24000 if is_neural else 16000,
                    is_neural=is_neural
                ))
            
            return voices
        except Exception as e:
            logger.error(f"Failed to get Google TTS voices: {e}")
            return []
    
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using Google Cloud TTS."""
        if not self.client:
            raise ValueError("Google TTS service not configured")
        
        self.validate_request(request)
        
        try:
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=request.text)
            
            # Build voice selection
            voice = texttospeech.VoiceSelectionParams(
                language_code=request.voice_id.split('-')[0] + '-' + request.voice_id.split('-')[1],
                name=request.voice_id
            )
            
            # Configure audio output
            # Map our format to Google's format
            audio_format_map = {
                AudioFormat.MP3: texttospeech.AudioEncoding.MP3,
                AudioFormat.WAV: texttospeech.AudioEncoding.LINEAR16,
                AudioFormat.OGG: texttospeech.AudioEncoding.OGG_OPUS
            }
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=audio_format_map.get(
                    request.output_format, 
                    texttospeech.AudioEncoding.MP3
                ),
                speaking_rate=request.speed,
                pitch=request.pitch,
                volume_gain_db=self._volume_to_db(request.volume)
            )
            
            # Run synthesis in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
            )
            
            audio_data = response.audio_content
            
            # Estimate duration (rough calculation)
            word_count = len(request.text.split())
            estimated_duration = (word_count / 150) * 60 / request.speed
            
            return TTSResponse(
                audio_data=audio_data,
                duration=estimated_duration,
                file_size=len(audio_data),
                format=request.output_format.value,
                voice_used=request.voice_id,
                sample_rate=24000 if "WaveNet" in request.voice_id else 16000,
                metadata={
                    "provider": "google",
                    "model": "WaveNet" if "WaveNet" in request.voice_id else "Standard"
                }
            )
            
        except GoogleAPICallError as e:
            logger.error(f"Google TTS API error: {e}")
            raise Exception(f"Google TTS API error: {e.message}")
        except Exception as e:
            logger.error(f"Google TTS synthesis failed: {e}")
            raise
    
    async def get_voice_preview(self, voice_id: str) -> bytes:
        """Get voice preview audio."""
        preview_text = "Hello, this is a preview of my voice."
        request = TTSRequest(
            text=preview_text,
            voice_id=voice_id,
            output_format=AudioFormat.MP3
        )
        response = await self.synthesize(request)
        return response.audio_data
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Google TTS provider information."""
        return {
            "name": "Google Cloud Text-to-Speech",
            "description": "Google's cloud-based text-to-speech service with WaveNet voices",
            "capabilities": [
                "wavenet_voices",
                "neural2_voices",
                "ssml_support",
                "multiple_formats",
                "prosody_control",
                "multiple_languages",
                "standard_voices"
            ],
            "max_text_length": 5000,
            "supported_formats": [AudioFormat.MP3.value, AudioFormat.WAV.value, AudioFormat.OGG.value],
            "is_configured": bool(self.client)
        }
    
    def _volume_to_db(self, volume: float) -> float:
        """Convert volume (0.0-2.0) to decibels."""
        if volume <= 0:
            return -96.0  # Mute
        # Convert linear volume to dB (reference 0 dB = volume 1.0)
        return 20 * (volume - 1.0)  # Range: -20dB to +20dB
