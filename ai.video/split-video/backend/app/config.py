from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8801
    
    # LLM Configuration
    llm_provider: str = "qwen"  # "qwen" for Qwen API or "ollama" for local
    
    # Qwen API Configuration
    qwen_api_key: str = ""
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen3-vl-32b-instruct"
    
    # Ollama Configuration (for local deployment)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3-vl-32b-instruct"
    
    # Whisper Configuration
    whisper_model: str = "base"
    
    # Video Processing Configuration
    target_chapter_duration: int = 600  # 10 minutes
    min_chapter_duration: int = 300     # 5 minutes
    max_chapter_duration: int = 900     # 15 minutes
    
    # Storage Configuration
    data_path: Path = Path("./data")
    upload_path: Path = Path("./data/uploads")
    processed_path: Path = Path("./data/processed")
    temp_path: Path = Path("./data/temp")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_path.mkdir(exist_ok=True)
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
