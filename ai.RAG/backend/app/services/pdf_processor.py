import os
import uuid
from pathlib import Path
from typing import List, Dict
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config import settings


class PDFProcessor:
    """PDF processing service for text extraction and chunking"""

    def __init__(self):
        self.storage_path = settings.get_pdf_storage_path()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    async def save_pdf(self, file_content: bytes, filename: str) -> Dict[str, str]:
        """
        Save PDF file to storage

        Args:
            file_content: PDF file content as bytes
            filename: Original filename

        Returns:
            Dict with document_id and saved filename
        """
        # Generate unique document ID
        doc_id = str(uuid.uuid4())

        # Create safe filename with UUID
        file_extension = Path(filename).suffix
        safe_filename = f"{doc_id}{file_extension}"
        file_path = self.storage_path / safe_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        return {
            "document_id": doc_id,
            "filename": safe_filename,
            "original_filename": filename,
            "file_path": str(file_path)
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        text = ""

        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

        return text

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks

        Args:
            text: Text content to split

        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        return chunks

    async def process_pdf(self, file_path: str, document_id: str) -> List[Dict[str, str]]:
        """
        Process PDF: extract text and create chunks

        Args:
            file_path: Path to PDF file
            document_id: Unique document identifier

        Returns:
            List of chunks with metadata
        """
        # Extract text
        text = self.extract_text_from_pdf(file_path)

        if not text.strip():
            raise ValueError("No text content found in PDF")

        # Split into chunks
        chunks = self.chunk_text(text)

        # Create chunk objects with metadata
        chunk_objects = []
        for idx, chunk in enumerate(chunks):
            chunk_objects.append({
                "document_id": document_id,
                "chunk_id": f"{document_id}_chunk_{idx}",
                "chunk_index": idx,
                "text": chunk,
                "total_chunks": len(chunks)
            })

        return chunk_objects

    def delete_pdf(self, filename: str) -> bool:
        """
        Delete PDF file from storage

        Args:
            filename: Filename to delete

        Returns:
            True if deleted successfully
        """
        file_path = self.storage_path / filename

        if file_path.exists():
            os.remove(file_path)
            return True

        return False

    def list_pdfs(self) -> List[Dict[str, str]]:
        """
        List all PDF files in storage

        Returns:
            List of PDF file information
        """
        pdfs = []

        for file_path in self.storage_path.glob("*.pdf"):
            pdfs.append({
                "filename": file_path.name,
                "document_id": file_path.stem,
                "file_size": file_path.stat().st_size,
                "modified_time": file_path.stat().st_mtime
            })

        return pdfs


# Global instance
pdf_processor = PDFProcessor()
