"""Text document loader"""
from pathlib import Path


class TextLoader:
    """Loader for plain text documents (TXT, MD)"""

    @staticmethod
    def load_from_path(file_path: Path) -> str:
        """Load plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def load_from_bytes(content: bytes, encoding: str = 'utf-8') -> str:
        """Load text from bytes"""
        return content.decode(encoding)
