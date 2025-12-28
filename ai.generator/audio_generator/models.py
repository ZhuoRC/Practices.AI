"""
音频生成数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AudioSegment(BaseModel):
    """音频段落模型"""
    index: int
    text: str
    file_path: Optional[str] = None
    duration: Optional[float] = None
    voice: str
    provider: str
    file_size: Optional[int] = None
    quality_score: Optional[float] = None
    status: str = "pending"  # pending, generating, completed, failed
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class AudioGenerationRequest(BaseModel):
    """音频生成请求"""
    project_id: str
    segments: List[Dict[str, Any]]  # 包含text, index等信息的段落列表
    provider: str = "azure"  # azure, elevenlabs, google
    voice: Optional[str] = None
    language: str = "zh"
    output_format: str = "mp3"  # wav, mp3
    quality: str = "high"  # low, medium, high
    rate: int = 22050  # 采样率
    batch_size: int = 5  # 批量处理大小
    output_dir: Optional[str] = None  # 自定义输出目录


class AudioGenerationResponse(BaseModel):
    """音频生成响应"""
    project_id: str
    status: str
    segments: List[AudioSegment]
    total_duration: float
    processing_time: float
    metadata: Dict[str, Any] = {}


class VoiceInfo(BaseModel):
    """语音信息"""
    id: str
    name: str
    language: str
    gender: str
    description: Optional[str] = None


class ProviderInfo(BaseModel):
    """TTS提供商信息"""
    provider_id: str
    provider_name: str
    available: bool
    voices: List[VoiceInfo]
    features: List[str]  # 支持的功能列表
