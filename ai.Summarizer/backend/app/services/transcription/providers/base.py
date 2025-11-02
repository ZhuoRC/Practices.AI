"""Base protocol for transcription providers"""
from typing import Protocol, Dict, Any, Optional, Callable


class TranscriptionProvider(Protocol):
    """Protocol defining the interface for transcription providers"""

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension for context

        Returns:
            Dictionary containing:
                - text: Transcribed text
                - language: Detected/specified language
                - duration: Audio duration in seconds
                - provider: Provider name
                - model: Model name
                - processing_time: Processing time in seconds
        """
        ...

    async def transcribe_async(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        file_extension: str = ".wav",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio with progress updates.

        Args:
            audio_data: Raw audio file bytes
            language: Optional language code
            file_extension: File extension
            progress_callback: Optional callback for progress updates

        Returns:
            Transcription result dictionary
        """
        ...
