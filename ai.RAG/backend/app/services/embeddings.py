from typing import List
import torch
from sentence_transformers import SentenceTransformer
from ..config import settings


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""

    def __init__(self):
        """Initialize the embedding model"""
        print(f"Loading embedding model: {settings.embedding_model}")

        # Detect and use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self.model = SentenceTransformer(settings.embedding_model, device=self.device)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.embedding_dimension}")

        # Set batch size based on device and config
        self.batch_size = settings.embedding_batch_size_gpu if self.device == "cuda" else settings.embedding_batch_size_cpu
        print(f"Batch size: {self.batch_size}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(
            text,
            convert_to_tensor=False,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        print(f"[Embedding] {len(texts)} texts | batch_size={self.batch_size}")
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_tensor=False,
            normalize_embeddings=True,
            show_progress_bar=True if len(texts) > 10 else False
        )
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.embedding_dimension


# Global instance
embedding_service = EmbeddingService()
