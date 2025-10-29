from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # LLM Configuration
    llm_provider: str = Field(default="cloud", env="LLM_PROVIDER")  # "cloud" or "local"

    # Qwen API Configuration (DashScope)
    qwen_api_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", env="QWEN_API_BASE_URL")
    qwen_api_key: str = Field(default="", env="QWEN_API_KEY")
    qwen_model: str = Field(default="qwen3-32b", env="QWEN_MODEL")

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen2.5:7b-instruct", env="OLLAMA_MODEL")

    # ChromaDB Configuration
    chroma_persist_directory: str = Field(default="../data/chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    chroma_collection_name: str = Field(default="documents", env="CHROMA_COLLECTION_NAME")

    # PDF Storage
    pdf_storage_path: str = Field(default="../data/pdfs", env="PDF_STORAGE_PATH")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8001, env="PORT")

    # Embedding Model
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )

    # Text Chunking
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")

    # RAG Configuration
    top_k: int = Field(default=3, env="TOP_K")  # Number of chunks to retrieve
    prompt_template_file: str = Field(
        default="rag_system.txt",
        env="PROMPT_TEMPLATE_FILE"
    )  # Name of the prompt template file in app/prompts/

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_pdf_storage_path(self) -> Path:
        """Get PDF storage path as Path object"""
        path = Path(self.pdf_storage_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_chroma_persist_directory(self) -> Path:
        """Get ChromaDB persist directory as Path object"""
        path = Path(self.chroma_persist_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
