"""Document loaders for various file formats"""
from pathlib import Path
from typing import Optional

from .base import DocumentLoader as BaseLoader
from .pdf_loader import PDFLoader
from .docx_loader import DOCXLoader
from .text_loader import TextLoader
from .webpage_loader import WebpageLoader


# Export individual loaders
__all__ = ['PDFLoader', 'DOCXLoader', 'TextLoader', 'WebpageLoader', 'DocumentLoader']


class DocumentLoader:
    """
    Unified document loader facade for backwards compatibility.
    Routes to appropriate loader based on file type.
    """

    @staticmethod
    def load_text(file_path: Path) -> str:
        """Load plain text file"""
        return TextLoader.load_from_path(file_path)

    @staticmethod
    def load_text_from_bytes(content: bytes, encoding: str = 'utf-8') -> str:
        """Load text from bytes"""
        return TextLoader.load_from_bytes(content, encoding)

    @staticmethod
    def load_pdf(file_path: Path) -> str:
        """Load PDF file and extract text"""
        return PDFLoader.load_from_path(file_path)

    @staticmethod
    def load_pdf_from_bytes(content: bytes) -> str:
        """Load PDF from bytes and extract text"""
        return PDFLoader.load_from_bytes(content)

    @staticmethod
    def load_docx(file_path: Path) -> str:
        """Load DOCX file and extract text"""
        return DOCXLoader.load_from_path(file_path)

    @staticmethod
    def load_docx_from_bytes(content: bytes) -> str:
        """Load DOCX from bytes and extract text"""
        return DOCXLoader.load_from_bytes(content)

    @staticmethod
    def load_webpage(url: str, timeout: int = 30) -> str:
        """Load webpage and extract main text content"""
        return WebpageLoader.load_from_url(url, timeout)

    @staticmethod
    def load_document(file_path: Path, file_type: Optional[str] = None) -> str:
        """
        Load document based on file extension

        Args:
            file_path: Path to the document
            file_type: Optional file type override (pdf, txt, docx)

        Returns:
            Extracted text content
        """
        if file_type is None:
            file_type = file_path.suffix.lower()

        if file_type in ['.txt', '.md', '.text']:
            return TextLoader.load_from_path(file_path)
        elif file_type == '.pdf':
            return PDFLoader.load_from_path(file_path)
        elif file_type in ['.docx', '.doc']:
            return DOCXLoader.load_from_path(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def load_document_from_bytes(content: bytes, file_type: str) -> str:
        """
        Load document from bytes based on file type

        Args:
            content: File content as bytes
            file_type: File extension (e.g., '.pdf', '.txt', '.docx')

        Returns:
            Extracted text content
        """
        file_type = file_type.lower()

        if file_type in ['.txt', '.md', '.text']:
            return TextLoader.load_from_bytes(content)
        elif file_type == '.pdf':
            return PDFLoader.load_from_bytes(content)
        elif file_type in ['.docx', '.doc']:
            return DOCXLoader.load_from_bytes(content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
