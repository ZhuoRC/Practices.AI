"""Map-Reduce document summarization service"""
from typing import Dict, Any, List
from pathlib import Path
import time
from .loaders import DocumentLoader
from .chunker import TextChunker
from .llm_client import get_llm_client
from ..config import settings


class MapReduceSummarizer:
    """Document summarization using Map-Reduce approach"""

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            min_size=settings.min_chunk_size,
            max_size=settings.max_chunk_size,
            overlap=settings.chunk_overlap
        )
        self.llm_client = get_llm_client()

    def summarize_document(
        self,
        content: bytes,
        file_type: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Summarize a document using Map-Reduce approach

        Args:
            content: Document content as bytes
            file_type: File extension (e.g., '.pdf', '.txt')
            filename: Original filename

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        # Step 1: Load document
        print(f"Loading document: {filename}")
        text = self.loader.load_document_from_bytes(content, file_type)
        original_length = len(text)
        print(f"Document loaded: {original_length} characters")

        if not text.strip():
            raise ValueError("Document is empty or could not be read")

        # Step 2: Chunk the text
        print("Chunking document...")
        chunks = self.chunker.create_chunks(text)
        print(f"Created {len(chunks)} chunks")

        if not chunks:
            raise ValueError("Failed to create chunks from document")

        # Step 3: Map phase - summarize each chunk
        print("Map phase: Summarizing chunks...")
        chunk_summaries = []
        chunk_details = []

        for i, chunk in enumerate(chunks):
            print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                summary = self.llm_client.summarize_chunk(
                    chunk_text=chunk['text'],
                    chunk_id=chunk['chunk_id'],
                    total_chunks=chunk['total_chunks']
                )
                chunk_summaries.append(summary)
                chunk_details.append({
                    'chunk_id': chunk['chunk_id'],
                    'length': chunk['length'],
                    'language': chunk['language'],
                    'summary': summary
                })
                print(f"  Chunk {i + 1} summarized ({len(summary)} chars)")
            except Exception as e:
                print(f"  Error summarizing chunk {i + 1}: {str(e)}")
                raise Exception(f"Failed to summarize chunk {i + 1}: {str(e)}")        # Step 4: Reduce phase - generate final summary
        print("Reduce phase: Generating final summary...")
        try:
            summaries_text = "

".join([
                f"片段 {i + 1} 摘要：
{summary}"
                for i, summary in enumerate(chunk_summaries)
            ])
            
            response = self.llm_client.generate(
                prompt=f"""请综合以下各个片段的摘要，生成一个完整、连贯的总摘要。

原文长度：约 {original_length} 字

各片段摘要：
{summaries_text}

要求：
1. 整合所有片段的关键信息
2. 生成逻辑连贯、结构清晰的总摘要
3. 总摘要长度约300-500字
4. 突出文档的主题和核心观点
5. 如果有明显的结构（如引言、正文、结论），请体现出来

总摘要：""",
                system_message="你是一个专业的文档摘要助手。请综合多个片段的摘要，生成一个连贯完整的总摘要。",
                temperature=0.6,
                max_tokens=1000
            )
            final_summary = response["text"].strip()
            
            # Add final summary tokens
            total_tokens["prompt_tokens"] += response["usage"]["prompt_tokens"]
            total_tokens["completion_tokens"] += response["usage"]["completion_tokens"]
            total_tokens["total_tokens"] += response["usage"]["total_tokens"]
            
            print(f"Final summary generated ({len(final_summary)} chars)")
        except Exception as e:
            print(f"Error generating final summary: {str(e)}")
            raise Exception(f"Failed to generate final summary: {str(e)}")

        # Calculate processing time
        processing_time = time.time() - start_time

        return {
            'filename': filename,
            'original_length': original_length,
            'num_chunks': len(chunks),
            'chunk_details': chunk_details,
            'chunk_summaries': chunk_summaries,
            'final_summary': final_summary,
            'processing_time': round(processing_time, 2),
            'model': self.llm_client.model,
            'provider': self.llm_client.provider,
            'token_usage': total_tokens
        }

    def summarize_webpage(self, url: str) -> Dict[str, Any]:
        """
        Summarize a webpage using Map-Reduce approach

        Args:
            url: Webpage URL

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        # Step 1: Load webpage
        print(f"Loading webpage: {url}")
        text = self.loader.load_webpage(url)
        original_length = len(text)
        print(f"Webpage loaded: {original_length} characters")

        if not text.strip():
            raise ValueError("Webpage is empty or could not be read")

        # Step 2: Chunk the text
        print("Chunking webpage content...")
        chunks = self.chunker.create_chunks(text)
        print(f"Created {len(chunks)} chunks")

        if not chunks:
            raise ValueError("Failed to create chunks from webpage")

        # Step 3: Map phase - summarize each chunk
        print("Map phase: Summarizing chunks...")
        chunk_summaries = []
        chunk_details = []
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for i, chunk in enumerate(chunks):
            print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                response = self.llm_client.generate(
                    prompt=f"""请为以下文本片段生成摘要。这是第 {chunk['chunk_id'] + 1}/{chunk['total_chunks']} 个片段。

文本内容：
{chunk['text']}

要求：
1. 提取主要观点和关键信息
2. 保持摘要简洁，约100-200字
3. 使用清晰的语言
4. 保留重要的数据、名称和术语

摘要：""",
                    system_message="你是一个专业的文档摘要助手。请仔细阅读文本，提取关键信息并生成简洁准确的摘要。",
                    temperature=0.5,
                    max_tokens=500
                )
                summary = response["text"].strip()
                
                # Accumulate token usage
                total_tokens["prompt_tokens"] += response["usage"]["prompt_tokens"]
                total_tokens["completion_tokens"] += response["usage"]["completion_tokens"]
                total_tokens["total_tokens"] += response["usage"]["total_tokens"]
                
                chunk_summaries.append(summary)
                chunk_details.append({
                    'chunk_id': chunk['chunk_id'],
                    'length': chunk['length'],
                    'language': chunk['language'],
                    'summary': summary
                })
            except Exception as e:
                raise Exception(f"Failed to summarize chunk {i + 1}: {str(e)}")

        # Step 4: Reduce phase - generate final summary
        print("Reduce phase: Generating final summary...")
        try:
            summaries_text = "

".join([
                f"片段 {i + 1} 摘要：
{summary}"
                for i, summary in enumerate(chunk_summaries)
            ])
            
            response = self.llm_client.generate(
                prompt=f"""请综合以下各个片段的摘要，生成一个完整、连贯的总摘要。

原文长度：约 {original_length} 字

各片段摘要：
{summaries_text}

要求：
1. 整合所有片段的关键信息
2. 生成逻辑连贯、结构清晰的总摘要
3. 总摘要长度约300-500字
4. 突出文档的主题和核心观点
5. 如果有明显的结构（如引言、正文、结论），请体现出来

总摘要：""",
                system_message="你是一个专业的文档摘要助手。请综合多个片段的摘要，生成一个连贯完整的总摘要。",
                temperature=0.6,
                max_tokens=1000
            )
            final_summary = response["text"].strip()
            
            # Add final summary tokens
            total_tokens["prompt_tokens"] += response["usage"]["prompt_tokens"]
            total_tokens["completion_tokens"] += response["usage"]["completion_tokens"]
            total_tokens["total_tokens"] += response["usage"]["total_tokens"]
        except Exception as e:
            raise Exception(f"Failed to generate final summary: {str(e)}")

        # Calculate processing time
        processing_time = time.time() - start_time

        return {
            'url': url,
            'original_length': original_length,
            'num_chunks': len(chunks),
            'chunk_details': chunk_details,
            'chunk_summaries': chunk_summaries,
            'final_summary': final_summary,
            'processing_time': round(processing_time, 2),
            'model': self.llm_client.model,
            'provider': self.llm_client.provider,
            'token_usage': total_tokens
        }


# Global summarizer instance
_summarizer: MapReduceSummarizer = None


def get_summarizer() -> MapReduceSummarizer:
    """Get or create global summarizer instance"""
    global _summarizer
    if _summarizer is None:
        _summarizer = MapReduceSummarizer()
    return _summarizer
