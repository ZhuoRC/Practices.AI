"""PDF document loader"""
import io
from pathlib import Path
import PyPDF2


class PDFLoader:
    """Loader for PDF documents"""

    @staticmethod
    def load_from_path(file_path: Path) -> str:
        """Load PDF file and extract text"""
        text = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)

    @staticmethod
    def load_from_bytes(content: bytes) -> str:
        """Load PDF from bytes and extract text"""
        text = []
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return '\n'.join(text)
