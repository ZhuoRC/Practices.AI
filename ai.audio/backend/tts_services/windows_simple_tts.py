"""
Windows Simple Text-to-Speech Implementation

This module provides a simple TTS implementation using Windows PowerShell
which is built into Windows and completely free. No additional dependencies required.
"""

import logging
import asyncio
import tempfile
import os
import subprocess
from typing import List, Dict, Any
from pathlib import Path

from .base import TTSService, TTSRequest, TTSResponse, VoiceInfo, AudioFormat

logger = logging.getLogger(__name__)


class WindowsSimpleTTSService(TTSService):
    """Windows PowerShell TTS implementation (no dependencies required)."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.default_voice = config.get("WINDOWS_TTS_DEFAULT_VOICE", "Zira")

    async def health_check(self) -> bool:
        """Check if Windows PowerShell TTS is available."""
        try:
            # Test PowerShell TTS command with longer timeout
            test_cmd = [
                "powershell", "-Command",
                "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices().Count"
            ]
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0 and result.stdout.strip().isdigit()
        except Exception as e:
            logger.error(f"Windows PowerShell TTS health check failed: {e}")
            return False

    async def get_available_voices(self) -> List[VoiceInfo]:
        """Get available Windows voices using PowerShell."""
        try:
            # PowerShell command to get available voices
            ps_command = """
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.GetInstalledVoices() | ForEach-Object {
                $voice = $_.VoiceInfo
                Write-Output "$($voice.Name)|$($voice.Culture.Name)|$($voice.Gender)|$($voice.Age)"
            }
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Failed to get voices: {result.stderr}")
                return self._get_default_voices()

            voices = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        name = parts[0]
                        culture = parts[1]
                        gender = parts[2] if len(parts) > 2 else "Unknown"

                        voice_id = name.lower().replace(" ", "_").replace("-", "_")

                        # Map culture to language code
                        if "en-US" in culture:
                            language = "en-US"
                        elif "zh-CN" in culture:
                            language = "zh-CN"
                        else:
                            language = culture

                        voices.append(VoiceInfo(
                            voice_id=voice_id,
                            name=name,
                            language=language,
                            gender=gender,
                            description=f"Windows built-in voice: {name}",
                            sample_rate=22050,
                            is_neural=False
                        ))

            return voices if voices else self._get_default_voices()

        except Exception as e:
            logger.error(f"Failed to get Windows voices: {e}")
            return self._get_default_voices()

    def _get_default_voices(self) -> List[VoiceInfo]:
        """Get default voices that are commonly available on Windows."""
        return [
            VoiceInfo(
                voice_id="microsoft_zira_desktop",
                name="Microsoft Zira Desktop",
                language="en-US",
                gender="Female",
                description="Windows built-in US English female voice",
                sample_rate=22050,
                is_neural=False
            ),
            VoiceInfo(
                voice_id="microsoft_david_desktop",
                name="Microsoft David Desktop",
                language="en-US",
                gender="Male",
                description="Windows built-in US English male voice",
                sample_rate=22050,
                is_neural=False
            )
        ]

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech using Windows PowerShell TTS."""
        self.validate_request(request)

        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
                text_file.write(request.text)
                text_file_path = text_file.name

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
                audio_file_path = audio_file.name

            try:
                # PowerShell command to synthesize speech using file input
                ps_command = f'''
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

                # Find and set voice
                $voices = $synth.GetInstalledVoices()
                $targetVoice = $null

                foreach ($v in $voices) {{
                    if ($v.VoiceInfo.Name -like "*{request.voice_id}*" -or $v.VoiceInfo.Name -like "*{request.voice_id.replace('_', ' ')}*") {{
                        $targetVoice = $v.VoiceInfo
                        break
                    }}
                }}

                if ($targetVoice) {{
                    $synth.SelectVoice($targetVoice.Name)
                }}

                # Set rate and volume
                $synth.Rate = {int((request.speed - 1.0) * 10)}
                $synth.Volume = {int(request.volume * 100)}

                # Read text from file and synthesize
                $text = Get-Content -Path "{text_file_path}" -Raw
                $synth.SetOutputToWaveFile("{audio_file_path}")
                $synth.Speak($text)
                $synth.SetOutputToDefaultAudioDevice()
                '''

                # Run PowerShell command
                process = await asyncio.create_subprocess_exec(
                    "powershell", "-Command", ps_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)

                if process.returncode != 0:
                    error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                    raise Exception(f"PowerShell TTS failed: {error_msg}")

                # Read the generated audio
                with open(audio_file_path, 'rb') as f:
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
                        "model": "powershell",
                        "engine": "windows-powershell"
                    }
                )

            finally:
                # Clean up temporary files
                try:
                    os.unlink(text_file_path)
                    os.unlink(audio_file_path)
                except OSError:
                    pass

        except asyncio.TimeoutError:
            raise Exception("TTS synthesis timed out")
        except Exception as e:
            logger.error(f"Windows PowerShell TTS synthesis failed: {e}")
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
            "name": "Windows PowerShell TTS",
            "description": "Built-in Windows text-to-speech using PowerShell and .NET",
            "capabilities": ["text-to-speech", "voice-selection", "speed-control", "volume-control"],
            "max_text_length": 10000,
            "supported_formats": ["wav"],
            "is_configured": True,
            "is_free": True,
            "is_offline": True
        }