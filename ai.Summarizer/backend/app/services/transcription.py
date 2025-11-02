"""
Transcription service for audio files using OpenAI Whisper (local).
"""
import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional
import whisper

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio to text using local Whisper model."""

    def __init__(self, model_name: str = "base"):
        """
        Initialize transcription service.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self._model = None
        logger.info(f"TranscriptionService initialized with model: {model_name}")

    @property
    def model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
            logger.info(f"Whisper model {self.model_name} loaded successfully")
        return self._model

    @staticmethod
    def _safe_delete_temp_file(temp_path: Path, max_retries: int = 3, delay: float = 0.5):
        """
        Safely delete a temporary file with retry logic for Windows file locking.

        Args:
            temp_path: Path to temporary file
            max_retries: Maximum number of deletion attempts
            delay: Delay between retries in seconds
        """
        for attempt in range(max_retries):
            try:
                if temp_path.exists():
                    temp_path.unlink()
                    logger.debug(f"Temp file deleted: {temp_path}")
                return
            except PermissionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to delete temp file (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to delete temp file after {max_retries} attempts: {temp_path}")
            except Exception as e:
                logger.warning(f"Error deleting temp file: {e}")
                return

    def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav"
    ) -> Dict[str, any]:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code (e.g., 'en', 'zh'). Auto-detect if None.
            file_extension: File extension for temp file (e.g., '.wav', '.mp3')

        Returns:
            Dictionary containing:
                - text: Transcribed text
                - language: Detected/specified language
                - duration: Audio duration in seconds

        Raises:
            Exception: If transcription fails
        """
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(
                suffix=file_extension,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(audio_data)

            logger.info(f"Transcribing audio file (temp: {temp_path})")

            # Transcribe using Whisper
            result = self.model.transcribe(
                str(temp_path),
                language=language,
                verbose=False
            )

            transcription_result = {
                "text": result["text"].strip(),
                "language": result.get("language", language or "unknown"),
                "duration": result.get("duration", 0.0)
            }

            logger.info(
                f"Transcription completed: {len(transcription_result['text'])} chars, "
                f"language: {transcription_result['language']}, "
                f"duration: {transcription_result['duration']:.2f}s"
            )

            return transcription_result

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
        finally:
            # Clean up temp file (with retry logic for Windows)
            self._safe_delete_temp_file(temp_path)

    async def transcribe_async(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav"
    ) -> Dict[str, any]:
        """
        Async wrapper for transcription (runs in thread pool).

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension for temp file

        Returns:
            Transcription result dictionary
        """
        import asyncio
        from functools import partial

        # Run blocking transcribe in thread pool
        loop = asyncio.get_event_loop()
        transcribe_fn = partial(
            self.transcribe,
            audio_data=audio_data,
            language=language,
            file_extension=file_extension
        )

        return await loop.run_in_executor(None, transcribe_fn)
