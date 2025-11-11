"""
Azure Cognitive Services Text-to-Speech Implementation

This module provides Azure Speech Service TTS implementation.
"""

import logging
from typing import List, Dict, Any
import azure.cognitiveservices.speech as speechsdk
from io import BytesIO

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat


logger = logging.getLogger(__name__)


class AzureTTSService(TTSService):
    """Azure Cognitive Services TTS implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.speech_key = config.get("AZURE_SPEECH_KEY")
        self.speech_region = config.get("AZURE_SPEECH_REGION", "eastus")
        
        if not self.speech_key:
            logger.warning("Azure Speech key not configured")
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        ) if self.speech_key else None
    
    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices from Azure Speech Service."""
        if not self.speech_config:
            return []
        
        try:
            # Azure doesn't have a direct API to list voices in the SDK
            # We'll return common known voices
            voices = [
                VoiceInfo(
                    voice_id="en-US-AriaNeural",
                    name="Aria",
                    language="en-US",
                    gender="Female",
                    description="Natural female voice",
                    is_neural=True
                ),
                VoiceInfo(
                    voice_id="en-US-JennyNeural",
                    name="Jenny",
                    language="en-US",
                    gender="Female",
                    description="Natural female voice",
                    is_neural=True
                ),
                VoiceInfo(
                    voice_id="en-US-GuyNeural",
                    name="Guy",
                    language="en-US",
                    gender="Male",
                    description="Natural male voice",
                    is_neural=True
                ),
                VoiceInfo(
                    voice_id="en-GB-RyanNeural",
                    name="Ryan",
                    language="en-GB",
                    gender="Male",
                    description="British male voice",
                    is_neural=True
                ),
                VoiceInfo(
                    voice_id="zh-CN-XiaoxiaoNeural",
                    name="晓晓",
                    language="zh-CN",
                    gender="Female",
                    description="Chinese female voice",
                    is_neural=True
                ),
                VoiceInfo(
                    voice_id="zh-CN-YunyangNeural",
                    name="云扬",
                    language="zh-CN",
                    gender="Male",
                    description="Chinese male voice",
                    is_neural=True
                ),
            ]
            return voices
        except Exception as e:
            logger.error(f"Failed to get Azure voices: {e}")
            return []
    
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using Azure TTS."""
        if not self.speech_config:
            raise ValueError("Azure Speech service not configured")
        
        self.validate_request(request)
        
        try:
            # Configure speech synthesis
            self.speech_config.speech_synthesis_voice_name = request.voice_id
            
            # Set output format
            if request.output_format == AudioFormat.MP3:
                self.speech_config.speech_synthesis_output_format = speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMp3
            elif request.output_format == AudioFormat.WAV:
                self.speech_config.speech_synthesis_output_format = speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
            else:
                self.speech_config.speech_synthesis_output_format = speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMp3
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # We'll use a stream
            )
            
            # Build SSML with prosody controls
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="{request.voice_id}">
                    <prosody rate="{request.speed}" pitch="{request.pitch:+.0f}Hz" volume="{request.volume}">
                        {request.text}
                    </prosody>
                </voice>
            </speak>
            """.strip()
            
            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                
                # Get duration estimation (rough calculation)
                # Typical speech rate is ~150 words per minute
                word_count = len(request.text.split())
                estimated_duration = (word_count / 150) * 60 / request.speed
                
                return TTSResponse(
                    audio_data=audio_data,
                    duration=estimated_duration,
                    file_size=len(audio_data),
                    format=request.output_format.value,
                    voice_used=request.voice_id,
                    sample_rate=24000,
                    metadata={
                        "provider": "azure",
                        "model": "neural"
                    }
                )
            else:
                error_details = result.reason
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    error_details = f"Canceled: {cancellation_details.reason} - {cancellation_details.error_details}"
                raise Exception(f"Speech synthesis failed: {error_details}")
                
        except Exception as e:
            logger.error(f"Azure TTS synthesis failed: {e}")
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
        """Get Azure TTS provider information."""
        return {
            "name": "Azure Cognitive Services",
            "description": "Microsoft's cloud-based text-to-speech service",
            "capabilities": [
                "neural_voices",
                "ssml_support",
                "multiple_formats",
                "prosody_control",
                "multiple_languages"
            ],
            "max_text_length": 5000,
            "supported_formats": [AudioFormat.MP3.value, AudioFormat.WAV.value],
            "is_configured": bool(self.speech_key)
        }
