"""
Transcription manager that supports both local (Whisper) and cloud (Qwen3-ASR-Flash) providers.
"""
import logging
from typing import Dict, Optional
from .providers.whisper import TranscriptionService
from .providers.cloud_asr import CloudASRService
from ...config import settings

logger = logging.getLogger(__name__)


class TranscriptionManager:
    """
    Unified transcription service that supports multiple providers.
    Automatically selects the appropriate provider based on configuration.
    """

    def __init__(self):
        """Initialize transcription manager with both providers."""
        self.provider = settings.transcription_provider.lower()

        # Initialize local Whisper service
        self.local_service = TranscriptionService(
            model_name=settings.whisper_model,
            device=settings.whisper_device,
            precision=settings.whisper_precision
        )

        # Initialize cloud ASR service
        if self.provider == "cloud":
            self.cloud_service = CloudASRService(
                api_key=settings.qwen_api_key,
                api_base_url=settings.qwen_asr_api_base_url,
                model_name=settings.qwen_asr_model
            )
        else:
            self.cloud_service = None

        logger.info(f"TranscriptionManager initialized with provider: {self.provider}")

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav"
    ) -> Dict[str, any]:
        """
        Transcribe audio using the configured provider.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension

        Returns:
            Transcription result dictionary
        """
        if self.provider == "cloud":
            if not self.cloud_service:
                raise Exception("Cloud ASR service not initialized")
            return await self.cloud_service.transcribe(audio_data, language, file_extension)
        else:
            return await self.local_service.transcribe(audio_data, language, file_extension)

    async def transcribe_async(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, any]:
        """
        Async transcription with progress callback.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension
            progress_callback: Progress update callback

        Returns:
            Transcription result dictionary
        """
        if self.provider == "cloud":
            if not self.cloud_service:
                raise Exception("Cloud ASR service not initialized")
            return await self.cloud_service.transcribe_async(audio_data, language, file_extension, progress_callback)
        else:
            return await self.local_service.transcribe_async(audio_data, language, file_extension, progress_callback)

    def get_provider_info(self) -> Dict[str, any]:
        """
        Get information about the current transcription provider.

        Returns:
            Provider information dictionary
        """
        if self.provider == "cloud":
            if self.cloud_service:
                return self.cloud_service.get_health_status()
            else:
                return {
                    "provider": "cloud",
                    "status": "not_initialized",
                    "model": settings.qwen_asr_model
                }
        else:
            # Local Whisper provider info
            import torch
            return {
                "provider": "local",
                "status": "initialized",
                "model": settings.whisper_model,
                "device": settings.whisper_device,
                "precision": settings.whisper_precision,
                "cuda_available": torch.cuda.is_available(),
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            }

    def switch_provider(self, new_provider: str):
        """
        Switch transcription provider.

        Args:
            new_provider: New provider ('local' or 'cloud')
        """
        new_provider = new_provider.lower()
        if new_provider not in ["local", "cloud"]:
            raise ValueError("Provider must be 'local' or 'cloud'")

        old_provider = self.provider
        self.provider = new_provider

        # Initialize cloud service if switching to cloud
        if new_provider == "cloud" and not self.cloud_service:
            self.cloud_service = CloudASRService(
                api_key=settings.qwen_api_key,
                api_base_url=settings.qwen_asr_api_base_url,
                model_name=settings.qwen_asr_model
            )

        logger.info(f"Switched transcription provider: {old_provider} -> {new_provider}")

    def is_cloud_provider(self) -> bool:
        """Check if current provider is cloud-based."""
        return self.provider == "cloud"

    def is_local_provider(self) -> bool:
        """Check if current provider is local-based."""
        return self.provider == "local"