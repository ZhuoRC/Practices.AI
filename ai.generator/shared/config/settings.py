"""
配置管理
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # ==================== 基础配置 ====================
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    APP_NAME: str = "AI Generator"
    VERSION: str = "1.0.0"
    
    # ==================== 目录配置 ====================
    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    # 数据目录（用于存储JSON文件）
    DATA_DIR: Path = BASE_DIR / "data"
    
    # 输入目录
    INPUT_DIR: Path = BASE_DIR / "input"
    
    # 输出目录
    OUTPUT_DIR: Path = BASE_DIR / "output"
    
    # 临时目录
    TEMP_DIR: Path = BASE_DIR / "temp"
    
    # 日志目录
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # ==================== AI API配置 ====================
    # OpenAI配置（用于文本改写）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_BASE_URL: Optional[str] = None
    
    # Anthropic配置（备用）
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    ANTHROPIC_BASE_URL: Optional[str] = None
    
    # ==================== TTS配置 ====================
    # Azure TTS配置
    AZURE_TTS_KEY: Optional[str] = None
    AZURE_TTS_REGION: Optional[str] = None
    AZURE_TTS_VOICE: str = "zh-CN-XiaoxiaoNeural"
    
    # ElevenLabs配置
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE: str = "21m00Tcm4TlvDq8ikWAM"
    
    # ChatTTS配置（本地TTS）
    CHATTTS_ENABLED: bool = True
    CHATTTS_PATH: Optional[str] = None  # ChatTTS路径，如果为None则使用相对路径
    CHATTTS_USE_GPU: bool = False  # 是否使用GPU加速
    
    # ==================== 视频生成配置 ====================
    VIDEO_RESOLUTION: str = "1920x1080"
    VIDEO_FPS: int = 30
    VIDEO_CODEC: str = "libx264"
    VIDEO_QUALITY: int = 23  # CRF值 (0-51, 越低质量越高)
    VIDEO_PRESET: str = "medium"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    
    # ==================== FFmpeg配置 ====================
    FFMPEG_PATH: Optional[str] = None  # FFmpeg可执行文件路径
    
    # ==================== 脚本处理配置 ====================
    SCRIPT_DEFAULT_LANGUAGE: str = "zh"
    SCRIPT_MAX_SEGMENT_LENGTH: int = 200  # 最大段落长度
    SCRIPT_MIN_SEGMENT_LENGTH: int = 50   # 最小段落长度
    SCRIPT_ENABLE_REWRITE: bool = False   # 是否启用AI改写
    SCRIPT_ENABLE_SEGMENTATION: bool = True  # 是否启用智能分段
    
    # ==================== 音频生成配置 ====================
    AUDIO_OUTPUT_FORMAT: str = "wav"  # wav, mp3
    AUDIO_RATE: int = 22050  # 采样率
    AUDIO_QUALITY: str = "high"  # low, medium, high
    AUDIO_BATCH_SIZE: int = 5  # 批量处理大小
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.DATA_DIR,
            self.DATA_DIR / "projects",
            self.DATA_DIR / "segments",
            self.INPUT_DIR,
            self.OUTPUT_DIR,
            self.OUTPUT_DIR / "audio",
            self.OUTPUT_DIR / "video",
            self.OUTPUT_DIR / "final",
            self.TEMP_DIR,
            self.TEMP_DIR / "audio",
            self.TEMP_DIR / "video",
            self.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def ffmpeg_executable(self) -> Optional[str]:
        """获取FFmpeg可执行文件路径"""
        if self.FFMPEG_PATH:
            return self.FFMPEG_PATH
        
        # 尝试从项目目录查找
        local_ffmpeg = self.BASE_DIR / "ffmpeg" / "win_x64" / "ffmpeg.exe"
        if local_ffmpeg.exists():
            return str(local_ffmpeg)
        
        # 尝试从系统PATH查找
        import shutil
        return shutil.which("ffmpeg")


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
