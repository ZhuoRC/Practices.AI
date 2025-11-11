"""
Text-to-Speech Services Module

This module provides various TTS (Text-to-Speech) service implementations
including cloud-based and local TTS providers.
"""

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo
from .azure_tts import AzureTTSService
from .google_tts import GoogleTTSService
from .elevenlabs_tts import ElevenLabsTTSService
from .local_tts import LocalTTSService
from .windows_simple_tts import WindowsSimpleTTSService
from .xtts_v2_tts import XTTSV2TTSService

__all__ = [
    'TTSService',
    'TTSRequest',
    'TTSResponse',
    'VoiceInfo',
    'AzureTTSService',
    'GoogleTTSService',
    'ElevenLabsTTSService',
    'LocalTTSService',
    'WindowsSimpleTTSService',
    'XTTSV2TTSService'
]
