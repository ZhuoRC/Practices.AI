"""
Cloud-based speech recognition service using Qwen3-ASR-Flash.
Handles audio files of any length by chunking long files into 3-minute segments.
"""
import logging
import asyncio
import base64
import json
import time
import io
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import aiohttp
import aiofiles
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Qwen ASR API limits
MAX_AUDIO_DURATION_SECONDS = 180  # 3 minutes max per request
CHUNK_DURATION_SECONDS = 170  # Use 170 seconds to have some buffer


class CloudASRService:
    """Service for cloud-based speech recognition using Qwen3-ASR-Flash."""

    def __init__(self, api_key: str, api_base_url: str, model_name: str = "qwen3-asr-flash"):
        """
        Initialize cloud ASR service.

        Args:
            api_key: API key for Qwen service
            api_base_url: Base URL for Qwen API
            model_name: Model name for ASR
        """
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip('/')
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        logger.info(f"CloudASRService initialized with model: {model_name}")

    def _get_audio_duration(self, audio_data: bytes, file_extension: str) -> float:
        """
        Get the duration of audio in seconds.

        Args:
            audio_data: Raw audio bytes
            file_extension: File extension (e.g., '.mp3', '.wav')

        Returns:
            Duration in seconds
        """
        try:
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=file_extension.lstrip('.')
            )
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            logger.error(f"Failed to get audio duration: {str(e)}")
            raise Exception(f"Failed to analyze audio file: {str(e)}")

    def _split_audio_into_chunks(
        self,
        audio_data: bytes,
        file_extension: str,
        chunk_duration: int = CHUNK_DURATION_SECONDS
    ) -> List[Tuple[bytes, float, float]]:
        """
        Split audio into chunks of specified duration.

        Args:
            audio_data: Raw audio bytes
            file_extension: File extension
            chunk_duration: Duration of each chunk in seconds

        Returns:
            List of tuples: (chunk_bytes, start_time, end_time)
        """
        try:
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=file_extension.lstrip('.')
            )

            total_duration_ms = len(audio)
            chunk_duration_ms = chunk_duration * 1000
            chunks = []

            for start_ms in range(0, total_duration_ms, chunk_duration_ms):
                end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
                chunk = audio[start_ms:end_ms]

                # Export chunk to bytes
                buffer = io.BytesIO()
                chunk.export(buffer, format=file_extension.lstrip('.'))
                chunk_bytes = buffer.getvalue()

                chunks.append((
                    chunk_bytes,
                    start_ms / 1000.0,  # start time in seconds
                    end_ms / 1000.0     # end time in seconds
                ))

            logger.info(f"Split audio into {len(chunks)} chunks (duration: {chunk_duration}s each)")
            return chunks

        except Exception as e:
            logger.error(f"Failed to split audio: {str(e)}")
            raise Exception(f"Failed to split audio file: {str(e)}")

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav"
    ) -> Dict[str, any]:
        """
        Transcribe audio using cloud Qwen3-ASR-Flash API.
        Automatically handles long audio files by chunking them into 3-minute segments.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code (e.g., 'en', 'zh'). Auto-detect if None.
            file_extension: File extension for context

        Returns:
            Dictionary containing:
                - text: Transcribed text
                - language: Detected/specified language
                - duration: Audio duration in seconds
                - provider: 'cloud'
                - model: Model name
                - processing_time: Total processing time

        Raises:
            Exception: If transcription fails
        """
        start_time = time.time()

        try:
            # Get audio duration
            duration = self._get_audio_duration(audio_data, file_extension)
            logger.info(f"Audio duration: {duration:.2f} seconds")

            # If audio is short enough, transcribe directly
            if duration <= MAX_AUDIO_DURATION_SECONDS:
                logger.info("Audio within API limit, transcribing directly...")
                transcription_text = await self._transcribe_single_chunk(
                    audio_data, language, file_extension
                )
            else:
                # Split into chunks and transcribe each
                logger.info(f"Audio exceeds {MAX_AUDIO_DURATION_SECONDS}s limit, splitting into chunks...")
                chunks = self._split_audio_into_chunks(audio_data, file_extension)

                # Transcribe all chunks in parallel
                tasks = []
                for i, (chunk_data, start_sec, end_sec) in enumerate(chunks):
                    logger.info(f"Queuing chunk {i+1}/{len(chunks)}: {start_sec:.1f}s - {end_sec:.1f}s")
                    task = self._transcribe_single_chunk(chunk_data, language, file_extension)
                    tasks.append(task)

                # Wait for all chunks to complete
                logger.info(f"Transcribing {len(chunks)} chunks in parallel...")
                chunk_transcriptions = await asyncio.gather(*tasks)

                # Combine transcriptions
                transcription_text = " ".join(chunk_transcriptions)
                logger.info(f"Combined {len(chunks)} chunks into final transcription")

            processing_time = time.time() - start_time
            logger.info(f"Total transcription time: {processing_time:.2f}s")

            return {
                "text": transcription_text,
                "language": language or "auto",
                "duration": duration,
                "provider": "cloud",
                "model": self.model_name,
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise

    async def _transcribe_single_chunk(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav"
    ) -> str:
        """
        Transcribe a single audio chunk using cloud Qwen3-ASR-Flash API.
        This method handles only chunks under 3 minutes.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code (e.g., 'en', 'zh'). Auto-detect if None.
            file_extension: File extension for context

        Returns:
            Transcribed text string

        Raises:
            Exception: If transcription fails
        """
        start_time = time.time()

        try:
            # Encode audio data to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Prepare request payload for Qwen multimodal API
            payload = {
                "model": self.model_name,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "audio": f"data:audio/{file_extension.lstrip('.')};base64,{audio_base64}"
                                }
                            ]
                        }
                    ]
                }
            }

            logger.info(f"Sending audio to cloud ASR (size: {len(audio_data)} bytes, format: {file_extension})")

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/v1/services/aigc/multimodal-generation/generation",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Cloud ASR successful, processing time: {time.time() - start_time:.2f}s")

                        # Extract transcription from multimodal response
                        # Response format: {"output": {"choices": [{"message": {"content": [{"text": "..."}]}}]}}
                        output = result.get("output", {})
                        choices = output.get("choices", [{}])
                        message_content = choices[0].get("message", {}).get("content", [{}]) if choices else [{}]
                        transcription_text = message_content[0].get("text", "").strip() if message_content else ""

                        logger.info(f"Chunk transcription successful: {len(transcription_text)} chars in {time.time() - start_time:.2f}s")
                        return transcription_text
                    else:
                        error_text = await response.text()
                        logger.error(f"Cloud ASR API error {response.status}: {error_text}")
                        raise Exception(f"Cloud ASR API error: {response.status} - {error_text}")

        except aiohttp.ClientError as e:
            logger.error(f"Cloud ASR network error: {str(e)}")
            raise Exception(f"Cloud ASR network error: {str(e)}")
        except asyncio.TimeoutError:
            logger.error("Cloud ASR request timeout")
            raise Exception("Cloud ASR request timeout")
        except Exception as e:
            logger.error(f"Cloud ASR transcription failed: {str(e)}")
            raise Exception(f"Failed to transcribe audio with cloud ASR: {str(e)}")

    async def transcribe_async(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, any]:
        """
        Async wrapper for transcription with progress simulation.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension for temp file
            progress_callback: Optional callback for progress updates

        Returns:
            Transcription result dictionary
        """
        # Simulate progress during cloud processing
        if progress_callback:
            progress_task = asyncio.create_task(
                self._simulate_cloud_progress(progress_callback)
            )

        try:
            result = await self.transcribe(audio_data, language, file_extension)

            if progress_callback:
                progress_task.cancel()
                try:
                    await progress_task
                except asyncio.CancelledError:
                    pass

            return result

        except Exception:
            if progress_callback:
                progress_task.cancel()
            raise

    async def _simulate_cloud_progress(self, progress_callback: callable):
        """
        Simulate progress updates during cloud ASR processing.
        """
        import asyncio

        try:
            # Cloud ASR progress simulation
            phases = [
                (10, "Uploading audio to cloud service..."),
                (30, "Initializing Qwen3-ASR-Flash model..."),
                (50, "Processing audio with cloud ASR..."),
                (70, "Converting speech to text..."),
                (85, "Refining transcription results..."),
                (95, "Finalizing transcription...")
            ]

            for percent, message in phases:
                await asyncio.sleep(1)  # Cloud processing is usually faster
                await progress_callback(message, percent)

        except asyncio.CancelledError:
            # Task was cancelled (transcription completed)
            pass

    def get_health_status(self) -> Dict[str, any]:
        """
        Get health status of cloud ASR service.

        Returns:
            Health status dictionary
        """
        return {
            "provider": "cloud",
            "model": self.model_name,
            "api_base_url": self.api_base_url,
            "status": "configured",
            "api_key_configured": bool(self.api_key)
        }