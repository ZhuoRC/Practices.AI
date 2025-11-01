from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # LLM Configuration
    llm_provider: str = Field(default="cloud", env="LLM_PROVIDER")

    # Qwen API Configuration
    qwen_api_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        env="QWEN_API_BASE_URL"
    )
    qwen_api_key: str = Field(default="", env="QWEN_API_KEY")
    qwen_model: str = Field(default="qwen-turbo", env="QWEN_MODEL")

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen2.5:7b-instruct", env="OLLAMA_MODEL")

    # Document Storage
    document_storage_path: str = Field(default="../data/documents", env="DOCUMENT_STORAGE_PATH")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8002, env="PORT")

    # Chunking Configuration
    min_chunk_size: int = Field(default=800, env="MIN_CHUNK_SIZE")
    max_chunk_size: int = Field(default=1200, env="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, env="CHUNK_OVERLAP")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_document_storage_path(self) -> Path:
        """Get document storage path as Path object"""
        path = Path(self.document_storage_path)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
