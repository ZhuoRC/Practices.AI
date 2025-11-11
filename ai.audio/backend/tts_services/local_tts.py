"""
Local Text-to-Speech Implementation

This module provides local TTS implementation using Piper TTS.
"""

import logging
from typing import List, Dict, Any
import subprocess
import os
import asyncio
import tempfile
from pathlib import Path

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat


logger = logging.getLogger(__name__)


class LocalTTSService(TTSService):
    """Local TTS implementation using Piper TTS."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_path = config.get("LOCAL_TTS_MODEL_PATH", "./models")
        self.default_voice = config.get("LOCAL_TTS_DEFAULT_VOICE", "en-us-lessac-medium")
        self.piper_path = self._find_piper_executable()
        
        # Available local voices (Piper models)
        self.local_voices = {
            "en-us-lessac-medium": VoiceInfo(
                voice_id="en-us-lessac-medium",
                name="Lessac (Medium)",
                language="en-US",
                gender="Male",
                description="American English male voice",
                sample_rate=22050,
                is_neural=True
            ),
            "en-us-lessac-low": VoiceInfo(
                voice_id="en-us-lessac-low",
                name="Lessac (Low)",
                language="en-US",
                gender="Male",
                description="American English male voice (lower quality)",
                sample_rate=22050,
                is_neural=True
            ),
            "en-us-amy-medium": VoiceInfo(
                voice_id="en-us-amy-medium",
                name="Amy (Medium)",
                language="en-US",
                gender="Female",
                description="American English female voice",
                sample_rate=22050,
                is_neural=True
            ),
            "en-gb-lessac-medium": VoiceInfo(
                voice_id="en-gb-lessac-medium",
                name="Lessac (UK Medium)",
                language="en-GB",
                gender="Male",
                description="British English male voice",
                sample_rate=22050,
                is_neural=True
            ),
        }
    
    def _find_piper_executable(self) -> str:
        """Find Piper TTS executable."""
        # Common locations for Piper
        possible_paths = [
            "piper",
            "./piper",
            "./piper/piper",
            "/usr/local/bin/piper",
            "/usr/bin/piper"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--help"], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        logger.warning("Piper TTS executable not found. Please install Piper TTS.")
        return None
    
    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available local voices."""
        if not self.piper_path:
            logger.warning("Piper TTS not available")
            return []
        
        # Check which voice models are actually available
        available_voices = []
        model_dir = Path(self.model_path)
        
        for voice_id, voice_info in self.local_voices.items():
            # Check if model files exist
            model_file = model_dir / f"{voice_id}.onnx"
            if model_file.exists():
                available_voices.append(voice_info)
            else:
                # Try to find the model in common locations
                for search_path in [model_dir, Path("./models"), Path("/usr/share/piper")]:
                    model_file = search_path / f"{voice_id}.onnx"
                    if model_file.exists():
                        available_voices.append(voice_info)
                        break
        
        return available_voices
    
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using local Piper TTS."""
        if not self.piper_path:
            raise ValueError("Piper TTS not available")
        
        self.validate_request(request)
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
                text_file.write(request.text)
                text_file_path = text_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
                audio_file_path = audio_file.name
            
            try:
                # Build Piper command
                cmd = [
                    self.piper_path,
                    "--model", f"{self.model_path}/{request.voice_id}.onnx",
                    "--input_file", text_file_path,
                    "--output_file", audio_file_path
                ]
                
                # Add speed control if supported
                if request.speed != 1.0:
                    # Piper uses sentence length ratio for speed
                    # This is a simplified mapping
                    length_scale = 1.0 / request.speed
                    cmd.extend(["--length_scale", str(length_scale)])
                
                # Run synthesis in thread pool
                loop = asyncio.get_event_loop()
                process = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                )
                
                if process.returncode != 0:
                    error_msg = process.stderr or process.stdout
                    raise Exception(f"Piper synthesis failed: {error_msg}")
                
                # Read the generated audio
                with open(audio_file_path, 'rb') as f:
                    audio_data = f.read()
                
                # Get audio duration using librosa or estimate
                try:
                    import librosa
                    import soundfile as sf
                    
                    # Load audio to get duration
                    y, sr = sf.read(audio_file_path)
                    duration = len(y) / sr
                except ImportError:
                    # Fallback estimation
                    word_count = len(request.text.split())
                    duration = (word_count / 150) * 60 / request.speed
                
                # Convert format if needed
                if request.output_format != AudioFormat.WAV:
                    audio_data = await self._convert_audio_format(
                        audio_data, 
                        AudioFormat.WAV, 
                        request.output_format
                    )
                
                return TTSResponse(
                    audio_data=audio_data,
                    duration=duration,
                    file_size=len(audio_data),
                    format=request.output_format.value,
                    voice_used=request.voice_id,
                    sample_rate=22050,
                    metadata={
                        "provider": "local",
                        "model": "piper",
                        "engine": "piper-tts"
                    }
                )
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(text_file_path)
                    os.unlink(audio_file_path)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            raise Exception("TTS synthesis timed out")
        except Exception as e:
            logger.error(f"Local TTS synthesis failed: {e}")
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
        """Get local TTS provider information."""
        return {
            "name": "Local Piper TTS",
            "description": "Offline neural text-to-speech using Piper",
            "capabilities": [
                "offline_processing",
                "neural_voices",
                "fast_synthesis",
                "low_resource_usage",
                "privacy_focused"
            ],
            "max_text_length": 10000,  # Higher limit for local processing
            "supported_formats": [AudioFormat.WAV.value, AudioFormat.MP3.value],
            "is_configured": bool(self.piper_path),
            "model_path": self.model_path,
            "piper_path": self.piper_path
        }
    
    async def _convert_audio_format(self, audio_data: bytes, 
                                   input_format: AudioFormat, 
                                   output_format: AudioFormat) -> bytes:
        """Convert audio between formats."""
        if input_format == output_format:
            return audio_data
        
        try:
            import tempfile
            from pydub import AudioSegment
            
            # Write input audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{input_format.value}', delete=False) as input_file:
                input_file.write(audio_data)
                input_file_path = input_file.name
            
            try:
                # Load and convert audio
                audio = AudioSegment.from_file(input_file_path, format=input_format.value)
                
                # Export to desired format
                with tempfile.NamedTemporaryFile(suffix=f'.{output_format.value}', delete=False) as output_file:
                    output_file_path = output_file.name
                
                # Set export parameters based on format
                export_params = {"format": output_format.value}
                if output_format == AudioFormat.MP3:
                    export_params["bitrate"] = "128k"
                elif output_format == AudioFormat.OGG:
                    export_params["codec"] = "libvorbis"
                
                audio.export(output_file_path, **export_params)
                
                # Read converted audio
                with open(output_file_path, 'rb') as f:
                    converted_data = f.read()
                
                return converted_data
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(input_file_path)
                    os.unlink(output_file_path)
                except OSError:
                    pass
                    
        except ImportError:
            logger.warning("pydub not available for audio format conversion")
            # Return original data if conversion fails
            return audio_data
        except Exception as e:
            logger.error(f"Audio format conversion failed: {e}")
            return audio_data
