"""
脚本处理数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ScriptSegment(BaseModel):
    """脚本段落模型"""
    index: int
    title: Optional[str] = None
    original_text: str
    rewritten_text: Optional[str] = None
    estimated_duration: Optional[float] = None
    keywords: List[str] = []
    emotion: Optional[str] = None
    
    class Config:
        from_attributes = True


class ScriptProcessRequest(BaseModel):
    """脚本处理请求"""
    project_id: str
    script_text: str
    language: str = "zh"
    enable_rewrite: bool = True
    enable_segmentation: bool = True
    enable_keyword_extraction: bool = True
    segment_length: int = 200  # 每段大约200字
    voice_style: str = "neutral"  # neutral, cheerful, serious, etc.


class ScriptProcessResponse(BaseModel):
    """脚本处理响应"""
    project_id: str
    status: str
    segments: List[ScriptSegment]
    total_duration: float
    processing_time: float
    metadata: Dict[str, Any] = {}


class RewriteRequest(BaseModel):
    """文本改写请求"""
    text: str
    style: str = "professional"  # professional, casual, energetic, etc.
    target_length: Optional[int] = None


class SegmentationRequest(BaseModel):
    """文本分段请求"""
    text: str
    max_length: int = 200
    min_length: int = 50
    preserve_sentences: bool = True


class KeywordExtractionRequest(BaseModel):
    """关键词提取请求"""
    text: str
    max_keywords: int = 5
    language: str = "zh"


class EmotionDetectionRequest(BaseModel):
    """情感检测请求"""
    text: str
    language: str = "zh"
