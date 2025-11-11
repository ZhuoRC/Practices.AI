"""
Windows Native Text-to-Speech Implementation

This module provides TTS implementation using Windows SAPI (Speech API)
which is built into Windows and completely free.
"""

import logging
import asyncio
import tempfile
import os
from typing import List, Dict, Any
from pathlib import Path

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat

logger = logging.getLogger(__name__)


class WindowsTTSService(TTSService):
    """Windows SAPI TTS implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.default_voice = config.get("WINDOWS_TTS_DEFAULT_VOICE", "Zira")
        self.voices_cache = None

    async def health_check(self) -> bool:
        """Check if Windows SAPI is available."""
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            return True
        except ImportError:
            logger.warning("pywin32 not installed. Windows SAPI not available.")
            return False
        except Exception as e:
            logger.error(f"Windows SAPI health check failed: {e}")
            return False

    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available Windows voices."""
        if self.voices_cache:
            return self.voices_cache

        try:
            import win32com.client

            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = []

            # Get available voices
            voice_names = []
            for i in range(speaker.GetVoices().Count):
                voice = speaker.GetVoices().Item(i)
                voice_names.append(voice.GetDescription())

            # Create voice info objects
            for voice_name in voice_names:
                voice_id = voice_name.lower().replace(" ", "_").replace("-", "_")

                # Determine language from voice name
                if "english" in voice_name.lower() or "zira" in voice_name.lower() or "david" in voice_name.lower():
                    language = "en-US"
                    gender = "Female" if "zira" in voice_name.lower() else "Male"
                elif "chinese" in voice_name.lower() or "huihui" in voice_name.lower():
                    language = "zh-CN"
                    gender = "Female"
                else:
                    language = "en-US"  # Default
                    gender = "Unknown"

                voices.append(VoiceInfo(
                    voice_id=voice_id,
                    name=voice_name,
                    language=language,
                    gender=gender,
                    description=f"Windows built-in voice: {voice_name}",
                    sample_rate=22050,
                    is_neural=False
                ))

            self.voices_cache = voices
            return voices

        except Exception as e:
            logger.error(f"Failed to get Windows voices: {e}")
            return []

    def _get_voice_by_id(self, voice_id: str):
        """Get SAPI voice object by voice_id."""
        try:
            import win32com.client

            speaker = win32com.client.Dispatch("SAPI.SpVoice")

            # Find voice by name or ID
            for i in range(speaker.GetVoices().Count):
                voice = speaker.GetVoices().Item(i)
                voice_name = voice.GetDescription()
                test_id = voice_name.lower().replace(" ", "_").replace("-", "_")

                if test_id == voice_id.lower() or voice_name.lower() == voice_id.lower():
                    return voice

            # Fallback to default voice
            logger.warning(f"Voice '{voice_id}' not found, using default voice")
            return speaker.GetVoices().Item(0)

        except Exception as e:
            logger.error(f"Failed to get voice '{voice_id}': {e}")
            return None

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using Windows SAPI."""
        self.validate_request(request)

        try:
            import win32com.client

            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                # Create SpFileStream object to save to file
                file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
                format_type = 22  # SAFT22kHz16BitMono
                file_stream.Format.Type = format_type

                # Open file for writing
                file_stream.Open(temp_path, 3)  # SSFMCreateForWrite

                # Create voice and set output
                speaker = win32com.client.Dispatch("SAPI.Voice")
                voice = self._get_voice_by_id(request.voice_id)

                if voice:
                    speaker.Voice = voice

                # Set audio output to file
                speaker.AudioOutputStream = file_stream

                # Adjust rate and volume
                speaker.Rate = int((request.speed - 1.0) * 10)  # Convert speed to rate (-10 to 10)
                speaker.Volume = int(request.volume * 100)  # Convert volume (0-100)

                # Speak text
                speaker.Speak(request.text, 0)  # 0 = SVSFlagsAsync

                # Close file stream
                file_stream.Close()

                # Read the generated audio
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()

                # Get audio duration (estimate)
                words_per_minute = 150  # Average reading speed
                estimated_words = len(request.text.split())
                duration = (estimated_words / words_per_minute) * 60

                return TTSResponse(
                    audio_data=audio_data,
                    duration=duration,
                    file_size=len(audio_data),
                    format="wav",
                    voice_used=request.voice_id,
                    sample_rate=22050,
                    metadata={
                        "provider": "windows",
                        "model": "sapi",
                        "engine": "windows-sapi"
                    }
                )

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        except Exception as e:
            logger.error(f"Windows SAPI synthesis failed: {e}")
            raise

    async def get_voice_preview(self, voice_id: str) -> bytes:
        """Get voice preview audio."""
        preview_text = "Hello, this is a preview of my voice."
        request = TTSRequest(
            text=preview_text,
            voice_id=voice_id,
            output_format=AudioFormat.WAV
        )
        response = await self.synthesize(request)
        return response.audio_data

    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            "name": "Windows SAPI TTS",
            "description": "Built-in Windows text-to-speech using Speech API",
            "capabilities": ["text-to-speech", "voice-selection", "speed-control", "volume-control"],
            "max_text_length": 10000,
            "supported_formats": ["wav"],
            "is_configured": True,
            "is_free": True,
            "is_offline": True
        }