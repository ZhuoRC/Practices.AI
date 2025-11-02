"""Base interface for document loaders"""
from typing import Protocol
from pathlib import Path


class DocumentLoader(Protocol):
    """Protocol defining the interface for document loaders"""

    @staticmethod
    def load_from_path(file_path: Path) -> str:
        """Load document from file path and extract text"""
        ...

    @staticmethod
    def load_from_bytes(content: bytes) -> str:
        """Load document from bytes and extract text"""
        ...
