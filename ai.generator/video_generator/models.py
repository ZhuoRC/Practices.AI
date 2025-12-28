"""
视频生成数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VideoSegment(BaseModel):
    """视频段落模型"""
    index: int
    text: str
    keywords: List[str] = []
    file_path: Optional[str] = None
    duration: Optional[float] = None
    resolution: Optional[Dict[str, int]] = None
    fps: Optional[int] = None
    file_size: Optional[int] = None
    status: str = "pending"  # pending, generating, completed, failed
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class VideoGenerationRequest(BaseModel):
    """视频生成请求"""
    project_id: str
    segments: List[Dict[str, Any]]  # 包含text, index, keywords等信息的段落列表
    duration: float  # 每个段落的时长（秒）
    resolution: str = "1920x1080"  # 分辨率
    fps: int = 30  # 帧率
    background_style: str = "gradient"  # gradient, solid, particles, animated
    text_animation: str = "fade_in"  # fade_in, typewriter, slide_in, bounce
    highlight_keywords: bool = True
    font_family: str = "SimHei"  # 字体
    font_size: int = 48  # 字体大小
    font_color: str = "#FFFFFF"  # 字体颜色
    background_color: str = "#1A1A2E"  # 背景颜色
    audio_files: Optional[List[Optional[str]]] = None  # 音频文件路径列表（与segments对应，可以是None）
    merge_segments: bool = True  # 是否将所有段落合并为一个完整视频
    output_dir: Optional[str] = None  # 自定义输出目录


class VideoGenerationResponse(BaseModel):
    """视频生成响应"""
    project_id: str
    status: str
    segments: List[VideoSegment]
    total_duration: float
    processing_time: float
    metadata: Dict[str, Any] = {}


class VideoEffect(BaseModel):
    """视频效果"""
    effect_id: str
    name: str
    category: str  # transition, animation, background
    description: str


class RenderConfig(BaseModel):
    """渲染配置"""
    width: int
    height: int
    fps: int
    codec: str = "libx264"
    quality: int = 23  # CRF值
    audio_bitrate: str = "192k"
    preset: str = "medium"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
