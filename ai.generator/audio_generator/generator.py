"""
音频生成核心逻辑
"""
import time
import os
import sys
import asyncio
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment as PydubAudioSegment
import requests

from shared.config import get_settings
from .models import (
    AudioSegment,
    AudioGenerationRequest,
    AudioGenerationResponse,
    VoiceInfo,
    ProviderInfo
)

settings = get_settings()

# ChatTTS支持
chat_tts = None
chat_tts_available = False
try:
    # 添加ChatTTS到路径
    chattts_path = settings.CHATTTS_PATH or str(Path(__file__).parent.parent.parent / "ai.audio" / "local-tts" / "ChatTTS")
    if os.path.exists(chattts_path):
        sys.path.insert(0, chattts_path)
        import ChatTTS
        
        # 初始化ChatTTS
        if settings.CHATTTS_ENABLED:
            chat_tts = ChatTTS.Chat()
            print("正在加载ChatTTS模型...")
            if chat_tts.load(source="huggingface", device="cuda" if settings.CHATTTS_USE_GPU else "cpu"):
                chat_tts_available = True
                print("✓ ChatTTS模型加载成功")
            else:
                print("✗ ChatTTS模型加载失败")
except Exception as e:
    print(f"ChatTTS初始化失败: {e}")
    chat_tts_available = False


class AudioGenerator:
    """音频生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.azure_client = None
        self.elevenlabs_client = None
        
        # 初始化Azure TTS
        if settings.AZURE_TTS_KEY and settings.AZURE_TTS_REGION:
            self.azure_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_TTS_KEY,
                region=settings.AZURE_TTS_REGION
            )
            self.azure_config.speech_synthesis_voice_name = settings.AZURE_TTS_VOICE
        
        # 初始化ElevenLabs
        if settings.ELEVENLABS_API_KEY:
            self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY
            self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        # 检查Windows PowerShell TTS
        self.windows_tts_available = self._check_windows_tts()
    
    async def generate_audio(self, request: AudioGenerationRequest) -> AudioGenerationResponse:
        """
        生成音频
        """
        start_time = time.time()
        segments: List[AudioSegment] = []
        
        try:
            # 确定使用的提供商和语音
            # 优先级: ChatTTS > Windows > Azure > ElevenLabs
            provider = request.provider
            if provider == "auto":
                if chat_tts_available:
                    provider = "chattts"
                elif self.windows_tts_available:
                    provider = "windows"
                elif settings.AZURE_TTS_KEY:
                    provider = "azure"
                elif settings.ELEVENLABS_API_KEY:
                    provider = "elevenlabs"
                else:
                    provider = "windows"  # 默认尝试Windows
            
            voice = request.voice or self._get_default_voice(provider, request.language)
            
            # 批量处理段落
            for i in range(0, len(request.segments), request.batch_size):
                batch = request.segments[i:i + request.batch_size]
                
                # 生成批次中的每个段落
                for seg_info in batch:
                    text = seg_info.get('text', '')
                    index = seg_info.get('index', 0)
                    
                    # 生成音频
                    result = await self._generate_single_audio(
                        text=text,
                        voice=voice,
                        provider=provider,  # 使用实际选择的provider
                        language=request.language,
                        output_format=request.output_format,
                        index=index,
                        project_id=request.project_id,
                        output_dir=request.output_dir
                    )
                    
                    segments.append(result)
            
            # 计算总时长
            total_duration = sum(seg.duration or 0 for seg in segments)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            return AudioGenerationResponse(
                project_id=request.project_id,
                status="success",
                segments=segments,
                total_duration=total_duration,
                processing_time=processing_time,
                metadata={
                    "provider": request.provider,
                    "voice": voice,
                    "segment_count": len(segments),
                    "format": request.output_format,
                    "quality": request.quality
                }
            )
            
        except Exception as e:
            return AudioGenerationResponse(
                project_id=request.project_id,
                status="error",
                segments=segments,
                total_duration=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _generate_single_audio(
        self,
        text: str,
        voice: str,
        provider: str,
        language: str,
        output_format: str,
        index: int,
        project_id: str,
        output_dir: Optional[str] = None
    ) -> AudioSegment:
        """
        生成单个音频段落
        """
        try:
            # 生成文件路径
            filename = f"{project_id}_audio_{index:04d}.{output_format}"
            # 使用自定义输出目录或默认目录
            if output_dir:
                output_path = Path(output_dir) / "audio" / filename
            else:
                output_path = settings.OUTPUT_DIR / "audio" / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 根据提供商生成音频
            if provider == "azure":
                audio_data, duration = await self._generate_with_azure(text, voice, output_format)
            elif provider == "elevenlabs":
                audio_data, duration = await self._generate_with_elevenlabs(text, voice, output_format)
            elif provider == "windows":
                audio_data, duration = await self._generate_with_windows(text, voice, output_format)
            elif provider == "chattts":
                audio_data, duration = await self._generate_with_chattts(text, voice, output_format)
            else:
                raise ValueError(f"不支持的TTS提供商: {provider}")
            
            # 保存音频文件
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # 获取文件大小
            file_size = os.path.getsize(output_path)
            
            return AudioSegment(
                index=index,
                text=text,
                file_path=str(output_path),
                duration=duration,
                voice=voice,
                provider=provider,
                file_size=file_size,
                status="completed"
            )
            
        except Exception as e:
            return AudioSegment(
                index=index,
                text=text,
                voice=voice,
                provider=provider,
                status="failed",
                error_message=str(e)
            )
    
    async def _generate_with_azure(
        self,
        text: str,
        voice: str,
        output_format: str
    ) -> tuple[bytes, float]:
        """
        使用Azure TTS生成音频
        """
        # 设置输出格式
        if output_format == "wav":
            self.azure_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoPcm
            )
        elif output_format == "mp3":
            self.azure_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )
        
        # 创建合成器
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.azure_config, audio_config=None)
        
        # 生成语音
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # 获取音频数据
            audio_data = result.audio_data
            
            # 估算时长（Azure不直接返回时长，根据音频数据估算）
            duration = self._estimate_duration(audio_data, output_format)
            
            return audio_data, duration
        else:
            raise Exception(f"Azure TTS生成失败: {result.reason}")
    
    async def _generate_with_elevenlabs(
        self,
        text: str,
        voice: str,
        output_format: str
    ) -> tuple[bytes, float]:
        """
        使用ElevenLabs生成音频
        """
        url = f"{self.elevenlabs_base_url}/text-to-speech/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_data = response.content
            
            # 如果需要其他格式，进行转换
            if output_format != "mp3":
                audio_data = self._convert_audio_format(audio_data, "mp3", output_format)
            
            # 估算时长
            duration = self._estimate_duration(audio_data, output_format)
            
            return audio_data, duration
        else:
            raise Exception(f"ElevenLabs生成失败: {response.status_code} - {response.text}")
    
    def _convert_audio_format(
        self,
        audio_data: bytes,
        from_format: str,
        to_format: str
    ) -> bytes:
        """
        转换音频格式
        """
        try:
            # 使用pydub进行格式转换
            audio = PydubAudioSegment.from_file(audio_data, format=from_format)
            
            # 导出为目标格式
            if to_format == "wav":
                return audio.export(format="wav").read()
            elif to_format == "mp3":
                return audio.export(format="mp3", bitrate="128k").read()
            else:
                raise ValueError(f"不支持的音频格式: {to_format}")
                
        except Exception as e:
            print(f"音频格式转换失败: {e}")
            return audio_data
    
    def _estimate_duration(self, audio_data: bytes, output_format: str) -> float:
        """
        估算音频时长
        """
        try:
            # 使用pydub加载音频并获取时长
            audio = PydubAudioSegment.from_file(audio_data, format=output_format)
            return len(audio) / 1000.0  # 转换为秒
        except Exception as e:
            print(f"无法估算音频时长: {e}")
            # 根据数据大小估算（假设平均比特率）
            if output_format == "mp3":
                bitrate = 128000  # 128kbps
            else:
                bitrate = 256000  # 256kbps for WAV
            
            return (len(audio_data) * 8) / bitrate
    
    def _get_default_voice(self, provider: str, language: str) -> str:
        """
        获取默认语音
        """
        voice_mapping = {
            "azure": {
                "zh": "zh-CN-XiaoxiaoNeural",
                "en": "en-US-JennyNeural",
                "ja": "ja-JP-NanamiNeural"
            },
            "elevenlabs": {
                "zh": "21m00Tcm4TlvDq8ikWAM",  # Rachel (多语言)
                "en": "21m00Tcm4TlvDq8ikWAM",
                "ja": "21m00Tcm4TlvDq8ikWAM"
            }
        }
        
        return voice_mapping.get(provider, {}).get(language, settings.AZURE_TTS_VOICE)
    
    def _check_windows_tts(self) -> bool:
        """
        检查Windows PowerShell TTS是否可用
        """
        try:
            # 测试PowerShell TTS命令
            test_cmd = [
                "powershell", "-Command",
                "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices().Count"
            ]
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and result.stdout.strip().isdigit()
        except Exception:
            return False
    
    async def _generate_with_windows(
        self,
        text: str,
        voice: str,
        output_format: str
    ) -> tuple[bytes, float]:
        """
        使用Windows PowerShell TTS生成音频
        """
        import tempfile
        import json
        
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
            audio_file_path = audio_file.name
        
        # 创建临时文本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as text_file:
            text_file.write(text)
            text_file_path = text_file.name
        
        try:
            # PowerShell命令 - 使用文件避免编码问题
            ps_command = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            
            # 尝试设置中文语音
            $voices = $synth.GetInstalledVoices()
            $chineseVoice = $voices | Where-Object {{ $_.VoiceInfo.Name -like "*Chinese*" -or $_.VoiceInfo.Name -like "*Huihui*" -or $_.VoiceInfo.Name -like "*Kangkang*" }}
            if ($chineseVoice) {{
                $synth.SelectVoice($chineseVoice.VoiceInfo.Name)
            }}
            
            # 读取文本文件
            $textPath = "{text_file_path}"
            if (-not (Test-Path $textPath)) {{
                Write-Error "Text file not found: $textPath"
                exit 1
            }}
            $text = Get-Content $textPath -Encoding UTF8 -Raw
            if (-not $text) {{
                Write-Error "Text is empty"
                exit 1
            }}
            
            # 设置输出格式
            $synth.SetOutputToWaveFile("{audio_file_path}")
            
            # 合成语音
            $synth.Speak($text)
            
            # 恢复默认输出
            $synth.SetOutputToDefaultAudioDevice()
            
            # 输出成功信息
            Write-Output "SUCCESS"
            '''
            
            # 运行PowerShell命令
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            
            print(f"PowerShell返回码: {result.returncode}")
            print(f"PowerShell stdout: {result.stdout}")
            if result.stderr:
                print(f"PowerShell stderr: {result.stderr}")
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                raise Exception(f"Windows PowerShell TTS failed: {error_msg}")
            
            # 检查是否成功
            if "SUCCESS" not in result.stdout:
                raise Exception(f"Windows PowerShell TTS failed to generate audio")
            
            # 读取生成的音频
            if not os.path.exists(audio_file_path):
                raise Exception("Audio file was not created")
            
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            # 检查音频数据
            if len(audio_data) < 1000:
                raise Exception(f"Generated audio is too small: {len(audio_data)} bytes")
            
            # 使用pydub获取实际时长
            try:
                audio = PydubAudioSegment.from_file(audio_file_path)
                duration = len(audio) / 1000.0  # 转换为秒
            except Exception as e:
                # 如果无法获取时长，根据文本估算
                words_per_minute = 150
                estimated_words = len(text.split())
                duration = (estimated_words / words_per_minute) * 60
            
            # 如果需要转换格式
            if output_format != "wav":
                audio_data = self._convert_audio_format(audio_data, "wav", output_format)
            
            return audio_data, duration
            
        finally:
            # 清理临时文件
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except OSError:
                pass
            try:
                if os.path.exists(text_file_path):
                    os.unlink(text_file_path)
            except OSError:
                pass
    
    async def get_available_voices(self, provider: str) -> ProviderInfo:
        """
        获取可用的语音列表
        """
        voices: List[VoiceInfo] = []
        available = False
        
        if provider == "azure":
            voices = self._get_azure_voices()
            available = bool(settings.AZURE_TTS_KEY)
        elif provider == "elevenlabs":
            voices = await self._get_elevenlabs_voices()
            available = bool(settings.ELEVENLABS_API_KEY)
        
        return ProviderInfo(
            provider_id=provider,
            provider_name=provider.capitalize(),
            available=available,
            voices=voices,
            features=["text-to-speech", "multiple-languages", "multiple-voices"]
        )
    
    def _get_azure_voices(self) -> List[VoiceInfo]:
        """
        获取Azure可用的语音
        """
        # 返回一些常用的Azure语音
        return [
            VoiceInfo(
                id="zh-CN-XiaoxiaoNeural",
                name="晓晓",
                language="zh-CN",
                gender="Female",
                description="自然、亲切的女声"
            ),
            VoiceInfo(
                id="zh-CN-YunxiNeural",
                name="云希",
                language="zh-CN",
                gender="Male",
                description="沉稳、专业的男声"
            ),
            VoiceInfo(
                id="en-US-JennyNeural",
                name="Jenny",
                language="en-US",
                gender="Female",
                description="Natural, friendly female voice"
            )
        ]
    
    async def _get_elevenlabs_voices(self) -> List[VoiceInfo]:
        """
        获取ElevenLabs可用的语音
        """
        try:
            url = f"{self.elevenlabs_base_url}/voices"
            headers = {"xi-api-key": self.elevenlabs_api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                voices = []
                
                for voice in data.get("voices", [])[:10]:  # 限制返回前10个
                    voices.append(VoiceInfo(
                        id=voice["voice_id"],
                        name=voice["name"],
                        language=voice.get("labels", {}).get("language", "unknown"),
                        gender="unknown",
                        description=voice.get("description", "")
                    ))
                
                return voices
            else:
                return []
                
        except Exception as e:
            print(f"获取ElevenLabs语音列表失败: {e}")
            return []
    
    async def _generate_with_chattts(
        self,
        text: str,
        voice: str,
        output_format: str
    ) -> tuple[bytes, float]:
        """
        使用ChatTTS生成音频
        """
        if not chat_tts_available:
            raise Exception("ChatTTS不可用，请检查模型是否正确加载")
        
        try:
            # ChatTTS生成音频
            wavs = chat_tts.infer(
                text=[text],
                stream=False,
                lang="zh",
                skip_refine_text=False,
                use_decoder=True,
                do_text_normalization=True
            )
            
            # 获取音频数据
            if wavs and len(wavs) > 0:
                audio_array = wavs[0]
                
                # 转换为16-bit PCM WAV格式
                audio_array = (audio_array * 32767).astype(np.int16)
                
                # 创建WAV文件头
                import wave
                import io
                
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # 单声道
                    wav_file.setsampwidth(2)  # 16位
                    wav_file.setframerate(24000)  # ChatTTS采样率
                    wav_file.writeframes(audio_array.tobytes())
                
                audio_data = wav_buffer.getvalue()
                
                # 计算时长
                duration = len(audio_array) / 24000.0  # 24000是采样率
                
                # 如果需要转换格式
                if output_format != "wav":
                    audio_data = self._convert_audio_format(audio_data, "wav", output_format)
                
                return audio_data, duration
            else:
                raise Exception("ChatTTS未生成音频数据")
                
        except Exception as e:
            raise Exception(f"ChatTTS生成失败: {str(e)}")
