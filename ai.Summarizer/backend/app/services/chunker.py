"""Intelligent text chunking with sentence awareness"""
import re
from typing import List
from langdetect import detect
import jieba


class TextChunker:
    """Smart text chunker that respects sentence boundaries"""

    def __init__(self, min_size: int = 800, max_size: int = 1200, overlap: int = 100):
        """
        Initialize chunker

        Args:
            min_size: Minimum chunk size in characters
            max_size: Maximum chunk size in characters
            overlap: Number of characters to overlap between chunks
        """
        self.min_size = min_size
        self.max_size = max_size
        self.overlap = overlap

        # Chinese sentence delimiters
        self.chinese_delimiters = ['。', '！', '？', '；', '…']
        # English sentence delimiters
        self.english_delimiters = ['.', '!', '?', ';']

    def detect_language(self, text: str) -> str:
        """Detect if text is primarily Chinese or English"""
        try:
            # Try to detect language
            lang = detect(text[:1000])  # Sample first 1000 chars
            return 'zh' if lang == 'zh-cn' or lang == 'zh-tw' else 'en'
        except:
            # Fallback: check for Chinese characters
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text[:1000]))
            return 'zh' if chinese_chars > 100 else 'en'

    def split_into_sentences(self, text: str, language: str = 'zh') -> List[str]:
        """
        Split text into sentences based on language

        Args:
            text: Input text
            language: 'zh' for Chinese, 'en' for English

        Returns:
            List of sentences
        """
        if language == 'zh':
            # Split on Chinese sentence delimiters
            pattern = '([。！？；…])'
            parts = re.split(pattern, text)
            sentences = []
            for i in range(0, len(parts) - 1, 2):
                sentence = parts[i] + (parts[i + 1] if i + 1 < len(parts) else '')
                sentence = sentence.strip()
                if sentence:
                    sentences.append(sentence)
            # Handle last part if exists
            if len(parts) % 2 == 1 and parts[-1].strip():
                sentences.append(parts[-1].strip())
        else:
            # Split on English sentence delimiters
            # More sophisticated sentence splitting for English
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def create_chunks(self, text: str) -> List[dict]:
        """
        Create chunks from text with sentence awareness

        Args:
            text: Input text to chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []

        # Detect language
        language = self.detect_language(text)

        # Split into sentences
        sentences = self.split_into_sentences(text, language)

        if not sentences:
            return []

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds max_size and we have content
            if current_length + sentence_length > self.max_size and current_chunk:
                # Save current chunk if it meets minimum size
                chunk_text = ''.join(current_chunk)
                if len(chunk_text) >= self.min_size:
                    chunks.append({
                        'text': chunk_text,
                        'length': len(chunk_text),
                        'language': language
                    })

                    # Start new chunk with overlap
                    # Keep last few sentences for overlap
                    overlap_text = chunk_text[-self.overlap:] if len(chunk_text) > self.overlap else chunk_text
                    current_chunk = [overlap_text, sentence]
                    current_length = len(overlap_text) + sentence_length
                else:
                    # If chunk is too small, just add the sentence
                    current_chunk.append(sentence)
                    current_length += sentence_length
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add final chunk if it exists
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'length': len(chunk_text),
                'language': language
            })

        # Add chunk IDs
        for i, chunk in enumerate(chunks):
            chunk['chunk_id'] = i
            chunk['total_chunks'] = len(chunks)

        return chunks

    def chunk_text(self, text: str) -> List[str]:
        """
        Simple interface to get list of chunk texts

        Args:
            text: Input text

        Returns:
            List of chunk text strings
        """
        chunks = self.create_chunks(text)
        return [chunk['text'] for chunk in chunks]


def create_chunker(min_size: int = 800, max_size: int = 1200, overlap: int = 100) -> TextChunker:
    """Factory function to create a TextChunker instance"""
    return TextChunker(min_size=min_size, max_size=max_size, overlap=overlap)
