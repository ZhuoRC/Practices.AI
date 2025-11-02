"""
Transcription service for audio files using OpenAI Whisper (local).
"""
import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import whisper
import torch

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio to text using local Whisper model."""

    def __init__(self, model_name: str = "base", device: str = "auto", precision: str = "auto"):
        """
        Initialize transcription service.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device selection (auto, cpu, cuda)
            precision: Precision selection (auto, fp16, fp32)
        """
        self.model_name = model_name
        self.device_config = device.lower()
        self.precision_config = precision.lower()
        self._model = None
        self._actual_device = None
        self._actual_precision = None

        logger.info(f"TranscriptionService initialized: model={model_name}, device={device}, precision={precision}")

    def _detect_optimal_config(self) -> Tuple[str, str]:
        """
        Detect optimal device and precision configuration.

        Returns:
            Tuple of (actual_device, actual_precision)
        """
        # Determine device
        if self.device_config == "cuda":
            if torch.cuda.is_available():
                actual_device = "cuda"
                logger.info("CUDA device explicitly selected and available")
            else:
                actual_device = "cpu"
                logger.warning("CUDA device requested but not available, falling back to CPU")
        elif self.device_config == "cpu":
            actual_device = "cpu"
            logger.info("CPU device explicitly selected")
        else:  # auto
            if torch.cuda.is_available():
                actual_device = "cuda"
                logger.info("Auto-detection: CUDA available, using GPU acceleration")
            else:
                actual_device = "cpu"
                logger.info("Auto-detection: CUDA not available, using CPU")

        # Determine precision
        if actual_device == "cpu":
            # CPU doesn't support FP16, always use FP32
            if self.precision_config == "fp16":
                logger.warning("FP16 precision requested but not supported on CPU, using FP32")
            actual_precision = "fp32"
        else:  # CUDA device
            if self.precision_config == "fp32":
                actual_precision = "fp32"
                logger.info("FP32 precision explicitly selected")
            elif self.precision_config == "fp16":
                actual_precision = "fp16"
                logger.info("FP16 precision explicitly selected")
            else:  # auto
                actual_precision = "fp16"
                logger.info("Auto-detection: Using FP16 precision for better GPU performance")

        return actual_device, actual_precision

    @property
    def model(self):
        """Lazy load the Whisper model with intelligent device and precision selection."""
        if self._model is None:
            # Detect optimal configuration
            self._actual_device, self._actual_precision = self._detect_optimal_config()

            # Load model with correct parameter order
            logger.info(f"Loading Whisper model: {self.model_name} on {self._actual_device} with {self._actual_precision} precision")

            if self._actual_device == "cuda" and self._actual_precision == "fp16":
                # Suppress the FP16 warning since we're explicitly handling it
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
                    self._model = whisper.load_model(self.model_name, self._actual_device)
            else:
                self._model = whisper.load_model(self.model_name, self._actual_device)

            # Log successful loading with performance hints
            logger.info(f"[SUCCESS] Whisper model {self.model_name} loaded successfully")
            logger.info(f"[DEVICE] {self._actual_device.upper()}")
            logger.info(f"[PRECISION] {self._actual_precision.upper()}")

            if self._actual_device == "cpu":
                logger.info("[TIP] Install CUDA for faster transcription with GPU acceleration")
            else:
                logger.info("[GPU] GPU acceleration enabled for faster transcription")

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
            # Preprocess audio data for better recognition
            processed_audio_data = self._preprocess_audio(audio_data, file_extension)

            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(
                suffix=file_extension,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(processed_audio_data)

            logger.info(f"Transcribing audio file (temp: {temp_path})")

            # Transcribe using Whisper with optimized parameters
            transcription_options = {
                "language": language,
                "verbose": False,
                "temperature": 0.0,  # Reduce randomness (most important!)
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "condition_on_previous_text": True,
                "initial_prompt": None,
                "word_timestamps": False
            }

            result = self.model.transcribe(str(temp_path), **transcription_options)

            # Post-process the transcription result
            raw_text = result["text"].strip()
            cleaned_text = self._post_process_transcription(raw_text)

            transcription_result = {
                "text": cleaned_text,
                "language": result.get("language", language or "unknown"),
                "duration": result.get("duration", 0.0),
                "original_text": raw_text  # Keep original for debugging
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
        file_extension: str = ".wav",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, any]:
        """
        Async wrapper for transcription (runs in thread pool).

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension for temp file
            progress_callback: Optional callback for progress updates

        Returns:
            Transcription result dictionary
        """
        import asyncio
        from functools import partial

        # Create a progress-aware transcription function
        async def transcribe_with_progress():
            # Start progress simulation in background
            if progress_callback:
                # Start a background task to simulate progress during transcription
                progress_task = asyncio.create_task(
                    self._simulate_transcription_progress(progress_callback)
                )

            # Run actual transcription
            loop = asyncio.get_event_loop()
            transcribe_fn = partial(
                self.transcribe,
                audio_data=audio_data,
                language=language,
                file_extension=file_extension
            )

            try:
                result = await loop.run_in_executor(None, transcribe_fn)
                if progress_callback:
                    progress_task.cancel()  # Cancel progress simulation
                    try:
                        await progress_task
                    except asyncio.CancelledError:
                        pass
                return result
            except Exception:
                if progress_callback:
                    progress_task.cancel()
                raise

        return await transcribe_with_progress()

    def _post_process_transcription(self, text: str) -> str:
        """
        Post-process transcription to remove repetition and common errors.
        """
        if not text:
            return text

        # Split into sentences and process
        sentences = text.split('。')
        cleaned_sentences = []

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            sentence = sentence.strip()

            # Check for suspicious repetition patterns
            if self._is_suspicious_repetition(sentence, cleaned_sentences):
                logger.warning(f"Detected suspicious repetition: '{sentence}'")
                continue

            cleaned_sentences.append(sentence)

        # Join sentences
        result = '。'.join(cleaned_sentences)

        # Add final punctuation if needed
        if result and not result.endswith('。'):
            result += '。'

        logger.info(f"Post-processing: {len(text)} -> {len(result)} chars")
        return result

    def _is_suspicious_repetition(self, sentence: str, previous_sentences: list) -> bool:
        """
        Detect suspicious repetition patterns in transcription.
        """
        # Common problematic patterns
        suspicious_patterns = [
            '李宗盛演唱',
            '李宗盛詞曲',
            '《風水大白》',
            '詞曲.*演唱',
            '演唱.*詞曲'
        ]

        # Check for exact matches with previous sentences
        for prev_sentence in previous_sentences[-3:]:  # Check last 3 sentences
            if sentence == prev_sentence:
                return True

        # Check for suspicious patterns
        import re
        for pattern in suspicious_patterns:
            if re.search(pattern, sentence):
                # If suspicious pattern, also check if it's repetitive
                if len(sentence) < 20:  # Very short sentences with patterns are suspicious
                    return True

        # Check for high character repetition (>80% same characters)
        if len(sentence) > 10:
            unique_chars = set(sentence.replace(' ', ''))
            repetition_ratio = len(unique_chars) / len(sentence)
            if repetition_ratio < 0.3:  # Less than 30% unique characters
                return True

        return False

    def _preprocess_audio(self, audio_data: bytes, file_extension: str) -> bytes:
        """
        Preprocess audio data to improve transcription quality.
        """
        try:
            import io
            import numpy as np
            import librosa
            import soundfile as sf

            # Load audio with librosa
            audio_buffer = io.BytesIO(audio_data)
            y, sr = librosa.load(audio_buffer, sr=16000)  # Resample to 16kHz for Whisper

            # Apply preprocessing steps
            # 1. Normalize audio
            y = librosa.util.normalize(y)

            # 2. Remove silence (optional, can be noisy)
            # y, _ = librosa.effects.trim(y, top_db=20)

            # 3. Apply high-pass filter to remove low-frequency noise
            # (Simple implementation using librosa effects)
            if hasattr(librosa.effects, 'preemphasis'):
                y = librosa.effects.preemphasis(y)

            # 4. Convert back to bytes
            output_buffer = io.BytesIO()
            sf.write(output_buffer, y, sr, format='WAV')
            output_buffer.seek(0)

            processed_data = output_buffer.getvalue()
            logger.info(f"Audio preprocessing: {len(audio_data)} -> {len(processed_data)} bytes")

            return processed_data

        except ImportError as e:
            logger.warning(f"Audio preprocessing libraries not available: {e}")
            logger.warning("Install librosa and soundfile for better transcription quality")
            return audio_data
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return audio_data

    async def _simulate_transcription_progress(self, progress_callback: callable):
        """
        Simulate progress updates during transcription.
        Since Whisper doesn't provide progress callbacks, we simulate realistic progress.
        """
        import asyncio

        try:
            # Simulate different transcription phases with more realistic timing
            phases = [
                (45, "Loading Whisper model..."),
                (50, "Analyzing audio structure..."),
                (55, "Preparing audio segments..."),
                (60, "Processing audio segments..."),
                (65, "Converting speech to text (1/4)..."),
                (70, "Converting speech to text (2/4)..."),
                (75, "Converting speech to text (3/4)..."),
                (80, "Converting speech to text (4/4)..."),
                (85, "Refining transcription results..."),
                (90, "Finalizing transcription..."),
                (95, "Completing transcription...")
            ]

            for percent, message in phases:
                await asyncio.sleep(3)  # Wait 3 seconds between updates
                # Check if progress_callback is async, call accordingly
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(message, percent)
                else:
                    progress_callback(message, percent)

        except asyncio.CancelledError:
            # Task was cancelled (transcription completed)
            pass
