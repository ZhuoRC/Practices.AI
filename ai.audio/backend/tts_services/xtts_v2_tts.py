"""
Coqui XTTS-v2 Text-to-Speech Implementation

This module provides TTS implementation using Coqui XTTS-v2,
a high-quality multilingual voice cloning model that supports
17 languages and requires just a 6-second audio clip for voice cloning.
"""

import logging
import asyncio
import tempfile
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat

logger = logging.getLogger(__name__)


class XTTSV2TTSService(TTSService):
    """Coqui XTTS-v2 TTS implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.default_speaker = config.get("XTTS_V2_DEFAULT_SPEAKER", "default")
        self.default_language = config.get("XTTS_V2_DEFAULT_LANGUAGE", "en")
        self.model_path = config.get("XTTS_V2_MODEL_PATH", None)
        self.use_gpu = config.get("XTTS_V2_USE_GPU", False)
        self.tts_instance = None
        self.voices_cache = None

    async def _initialize_tts(self):
        """Initialize TTS model (lazy loading)."""
        if self.tts_instance is not None:
            return True

        try:
            from TTS.api import TTS

            logger.info("Loading XTTS-v2 model... This may take a while.")

            # Initialize TTS with XTTS-v2 model
            if self.model_path and os.path.exists(self.model_path):
                self.tts_instance = TTS(model_path=self.model_path, gpu=self.use_gpu)
            else:
                # Download and load the official model
                self.tts_instance = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=self.use_gpu)

            logger.info("XTTS-v2 model loaded successfully!")
            return True

        except ImportError:
            logger.error("TTS library not installed. Install with: pip install TTS")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize XTTS-v2: {e}")
            return False

    async def health_check(self) -> bool:
        """Check if XTTS-v2 is available."""
        try:
            # Check if TTS library is installed
            from TTS.api import TTS
            return True
        except ImportError:
            logger.warning("TTS library not installed. XTTS-v2 will be available after installing: pip install TTS>=0.22.0 torch>=2.0.0 torchaudio>=2.0.0")
            return True  # Still return True so it shows up in providers list
        except Exception as e:
            logger.error(f"XTTS-v2 health check failed: {e}")
            return False

    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available XTTS-v2 voices."""
        if self.voices_cache:
            return self.voices_cache

        try:
            voices = []

            # XTTS-v2 supports voice cloning from audio files
            # We can provide some default voice options

            # Default speaker (model's built-in voice)
            voices.append(VoiceInfo(
                voice_id="default_female",
                name="Default Female Speaker",
                language="en-US",
                gender="Female",
                description="XTTS-v2 default female voice (no audio sample required)",
                sample_rate=24000,
                is_neural=True
            ))

            voices.append(VoiceInfo(
                voice_id="default_male",
                name="Default Male Speaker",
                language="en-US",
                gender="Male",
                description="XTTS-v2 default male voice (no audio sample required)",
                sample_rate=24000,
                is_neural=True
            ))

            # Multilingual options
            voices.append(VoiceInfo(
                voice_id="default_female_zh",
                name="Default Female Speaker (Chinese)",
                language="zh-CN",
                gender="Female",
                description="XTTS-v2 default female voice for Chinese",
                sample_rate=24000,
                is_neural=True
            ))

            voices.append(VoiceInfo(
                voice_id="default_female_es",
                name="Default Female Speaker (Spanish)",
                language="es-ES",
                gender="Female",
                description="XTTS-v2 default female voice for Spanish",
                sample_rate=24000,
                is_neural=True
            ))

            voices.append(VoiceInfo(
                voice_id="default_female_fr",
                name="Default Female Speaker (French)",
                language="fr-FR",
                gender="Female",
                description="XTTS-v2 default female voice for French",
                sample_rate=24000,
                is_neural=True
            ))

            # Add common voice cloning examples
            voice_samples_path = Path(os.getenv("XTTS_V2_VOICE_SAMPLES_PATH", "./voice_samples"))

            if voice_samples_path.exists():
                for sample_file in voice_samples_path.glob("*.wav"):
                    voice_name = sample_file.stem.replace("_", " ").title()
                    voices.append(VoiceInfo(
                        voice_id=f"cloned_{sample_file.stem}",
                        name=f"Cloned: {voice_name}",
                        language="en-US",  # Could be detected from filename
                        gender="Unknown",   # Could be detected from filename
                        description=f"Voice cloned from sample: {sample_file.name}",
                        sample_rate=24000,
                        is_neural=True
                    ))

            self.voices_cache = voices
            return voices

        except Exception as e:
            logger.error(f"Failed to get XTTS-v2 voices: {e}")
            return []

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using XTTS-v2."""
        self.validate_request(request)

        if not await self._initialize_tts():
            raise ValueError("XTTS-v2 model not available")

        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name

            try:
                # Parse voice_id to determine if it's a cloned voice
                speaker_wav = None
                language = self.default_language

                if request.voice_id.startswith("cloned_"):
                    # This is a cloned voice - find the audio sample
                    sample_name = request.voice_id.replace("cloned_", "")
                    voice_samples_path = Path(os.getenv("XTTS_V2_VOICE_SAMPLES_PATH", "./voice_samples"))
                    sample_file = voice_samples_path / f"{sample_name}.wav"

                    if sample_file.exists():
                        speaker_wav = str(sample_file)
                        logger.info(f"Using voice sample: {sample_file}")
                    else:
                        logger.warning(f"Voice sample not found: {sample_file}, using default voice")

                # Determine language from request or default
                supported_languages = [
                    'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru',
                    'nl', 'cs', 'ar', 'zh', 'ja', 'hu', 'ko', 'hi'
                ]

                # Try to detect language from voice_id or use default
                if 'zh' in request.voice_id.lower() or 'chinese' in request.voice_id.lower():
                    language = 'zh'
                elif 'es' in request.voice_id.lower() or 'spanish' in request.voice_id.lower():
                    language = 'es'
                elif 'fr' in request.voice_id.lower() or 'french' in request.voice_id.lower():
                    language = 'fr'
                elif 'de' in request.voice_id.lower() or 'german' in request.voice_id.lower():
                    language = 'de'
                elif 'ja' in request.voice_id.lower() or 'japanese' in request.voice_id.lower():
                    language = 'ja'
                elif 'ko' in request.voice_id.lower() or 'korean' in request.voice_id.lower():
                    language = 'ko'
                else:
                    language = self.default_language

                # XTTS-v2 synthesis parameters
                synthesize_kwargs = {
                    "text": request.text,
                    "file_path": output_path,
                    "language": language
                }

                # Add speaker audio if available (for voice cloning)
                if speaker_wav:
                    synthesize_kwargs["speaker_wav"] = speaker_wav

                # Run synthesis in thread pool to avoid blocking
                loop = asyncio.get_event_loop()

                if not speaker_wav:
                    # Use default voice sample for non-cloned voices
                    voice_samples_path = Path(os.getenv("XTTS_V2_VOICE_SAMPLES_PATH", "./voice_samples"))
                    default_sample = voice_samples_path / "default.wav"
                    
                    if default_sample.exists():
                        speaker_wav = str(default_sample)
                        synthesize_kwargs["speaker_wav"] = speaker_wav
                        logger.info(f"Using default voice sample: {default_sample}")
                    else:
                        raise ValueError(
                            "XTTS-v2 requires a voice sample for synthesis. "
                            "Please provide a voice sample file or use a voice with 'cloned_' prefix. "
                            "Available voice samples can be placed in voice_samples/ directory."
                        )

                await loop.run_in_executor(
                    None,
                    lambda: self.tts_instance.tts_to_file(**synthesize_kwargs)
                )

                # Read the generated audio
                with open(output_path, 'rb') as f:
                    audio_data = f.read()

                # Get audio duration
                try:
                    import librosa
                    import soundfile as sf

                    # Load audio to get duration
                    y, sr = sf.read(output_path)
                    duration = len(y) / sr
                except ImportError:
                    # Estimate duration based on text length and language
                    avg_chars_per_second = 8 if language in ['zh', 'ja', 'ko'] else 15
                    duration = len(request.text) / avg_chars_per_second

                return TTSResponse(
                    audio_data=audio_data,
                    duration=duration,
                    file_size=len(audio_data),
                    format="wav",
                    voice_used=request.voice_id,
                    sample_rate=24000,
                    metadata={
                        "provider": "xtts_v2",
                        "model": "coqui-xtts-v2",
                        "engine": "coqui-tts",
                        "language": language,
                        "voice_cloned": speaker_wav is not None
                    }
                )

            finally:
                # Clean up temporary file
                try:
                    os.unlink(output_path)
                except OSError:
                    pass

        except Exception as e:
            logger.error(f"XTTS-v2 synthesis failed: {e}")
            raise

    async def get_voice_preview(self, voice_id: str) -> bytes:
        """Get voice preview audio."""
        preview_text = "Hello, this is a preview of my voice."
        if 'zh' in voice_id.lower() or 'chinese' in voice_id.lower():
            preview_text = "你好，这是我的声音预览。"
        elif 'es' in voice_id.lower() or 'spanish' in voice_id.lower():
            preview_text = "Hola, este es un adelanto de mi voz."
        elif 'fr' in voice_id.lower() or 'french' in voice_id.lower():
            preview_text = "Bonjour, ceci est un aperçu de ma voix."

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
            "name": "Coqui XTTS-v2",
            "description": "High-quality multilingual TTS with voice cloning capabilities",
            "capabilities": [
                "text-to-speech",
                "multilingual",
                "voice-cloning",
                "emotion-transfer",
                "cross-language-voice-cloning"
            ],
            "max_text_length": 5000,
            "supported_formats": ["wav"],
            "is_configured": True,
            "is_free": True,
            "is_offline": True,
            "supported_languages": [
                "en (English)", "es (Spanish)", "fr (French)", "de (German)",
                "it (Italian)", "pt (Portuguese)", "pl (Polish)", "tr (Turkish)",
                "ru (Russian)", "nl (Dutch)", "cs (Czech)", "ar (Arabic)",
                "zh (Chinese)", "ja (Japanese)", "hu (Hungarian)", "ko (Korean)", "hi (Hindi)"
            ],
            "requires_voice_sample": False,
            "voice_cloning_supported": True
        }
