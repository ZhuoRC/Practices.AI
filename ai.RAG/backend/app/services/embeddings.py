from typing import List
from sentence_transformers import SentenceTransformer
from ..config import settings


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""

    def __init__(self):
        """Initialize the embedding model"""
        print(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.embedding_dimension}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.embedding_dimension


# Global instance
embedding_service = EmbeddingService()
