import os
import uuid
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config import settings


class PDFProcessor:
    """PDF processing service for text extraction and chunking"""

    def __init__(self):
        self.storage_path = settings.get_pdf_storage_path()
        self.metadata_file = self.storage_path / "metadata.json"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self._load_metadata()

    def _load_metadata(self):
        """Load metadata from JSON file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata file: {e}")
                self.metadata = {}
        else:
            self.metadata = {}

    def _save_metadata(self):
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    async def save_pdf(self, file_content: bytes, filename: str) -> Dict[str, str]:
        """
        Save PDF file to storage with format: original_name_timestamp.pdf

        Args:
            file_content: PDF file content as bytes
            filename: Original filename

        Returns:
            Dict with document_id, stored filename, and original filename
        """
        # Generate unique document ID
        doc_id = str(uuid.uuid4())

        # Get original filename without extension
        original_name = Path(filename).stem
        file_extension = Path(filename).suffix

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Create filename with format: original_name_timestamp.pdf
        stored_filename = f"{original_name}_{timestamp}{file_extension}"
        file_path = self.storage_path / stored_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Save metadata
        upload_time = datetime.now().isoformat()
        self.metadata[doc_id] = {
            "original_filename": filename,
            "stored_filename": stored_filename,
            "upload_time": upload_time,
            "file_size": len(file_content)
        }
        self._save_metadata()

        return {
            "document_id": doc_id,
            "filename": stored_filename,
            "original_filename": filename,
            "file_path": str(file_path),
            "upload_time": upload_time
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
            filename: Filename or document_id to delete

        Returns:
            True if deleted successfully
        """
        # Check if it's a document_id
        if filename in self.metadata:
            stored_filename = self.metadata[filename]["stored_filename"]
            file_path = self.storage_path / stored_filename

            if file_path.exists():
                os.remove(file_path)

            # Remove from metadata
            del self.metadata[filename]
            self._save_metadata()
            return True

        # Otherwise treat as filename
        file_path = self.storage_path / filename

        if file_path.exists():
            os.remove(file_path)

            # Try to find and remove from metadata
            for doc_id, meta in list(self.metadata.items()):
                if meta["stored_filename"] == filename:
                    del self.metadata[doc_id]
                    self._save_metadata()
                    break

            return True

        return False

    def list_pdfs(self) -> List[Dict[str, str]]:
        """
        List all PDF files in storage

        Returns:
            List of PDF file information with original filenames
        """
        pdfs = []

        # Use metadata if available
        for doc_id, meta in self.metadata.items():
            stored_filename = meta["stored_filename"]
            file_path = self.storage_path / stored_filename

            if file_path.exists():
                # Parse upload_time to yyyy-mm-dd format
                upload_time = meta.get("upload_time", "")
                if upload_time:
                    try:
                        dt = datetime.fromisoformat(upload_time)
                        formatted_date = dt.strftime("%Y-%m-%d")
                    except:
                        formatted_date = upload_time
                else:
                    formatted_date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")

                pdfs.append({
                    "document_id": doc_id,
                    "filename": meta["original_filename"],  # Return original filename
                    "stored_filename": stored_filename,
                    "file_size": meta.get("file_size", file_path.stat().st_size),
                    "upload_time": formatted_date,
                    "modified_time": file_path.stat().st_mtime
                })

        # Handle files without metadata (legacy files)
        for file_path in self.storage_path.glob("*.pdf"):
            filename = file_path.name

            # Skip if already in metadata
            if any(meta["stored_filename"] == filename for meta in self.metadata.values()):
                continue

            # Legacy file without metadata
            formatted_date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
            pdfs.append({
                "document_id": file_path.stem,  # Use filename stem as doc_id for legacy files
                "filename": filename,
                "stored_filename": filename,
                "file_size": file_path.stat().st_size,
                "upload_time": formatted_date,
                "modified_time": file_path.stat().st_mtime
            })

        return pdfs


# Global instance
pdf_processor = PDFProcessor()
