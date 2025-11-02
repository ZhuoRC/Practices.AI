"""Map-Reduce document summarization service - Async Version"""
from typing import Dict, Any, List
from pathlib import Path
import time
from .loaders import DocumentLoader
from .chunker import TextChunker
from .llm_client import get_llm_client
from ..config import settings
from .prompt_templates import (
    get_chunk_summary_prompt,
    get_final_summary_prompt,
    CHUNK_SUMMARY_SYSTEM,
    FINAL_SUMMARY_SYSTEM
)
from .checkpoint import get_checkpoint_manager


class AsyncMapReduceSummarizer:
    """Document summarization using Map-Reduce approach with async processing"""

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            min_size=settings.min_chunk_size,
            max_size=settings.max_chunk_size,
            overlap=settings.chunk_overlap
        )
        self.llm_client = get_llm_client()

    async def summarize_document(
        self,
        content: bytes,
        file_type: str,
        filename: str,
        summary_length: int = 500
    ) -> Dict[str, Any]:
        """
        Summarize a document using Map-Reduce approach (async)

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

        # Step 2.5: Check for checkpoint and resume if available
        checkpoint_mgr = get_checkpoint_manager()
        task_id = checkpoint_mgr.find_checkpoint_by_content(content)

        checkpoint = None
        start_chunk_idx = 0

        if task_id:
            checkpoint = checkpoint_mgr.load_checkpoint(task_id)

        if checkpoint:
            # Resume from checkpoint
            chunk_summaries = checkpoint["chunk_summaries"]
            chunk_details = checkpoint["chunk_details"]
            total_tokens = checkpoint["total_tokens"]
            start_chunk_idx = len(chunk_summaries)
            print(f"  ⏭ Resuming from checkpoint: {start_chunk_idx}/{len(chunks)} chunks already completed")
            print(f"  💰 Saved tokens so far: {total_tokens['total_tokens']} tokens")
        else:
            # Fresh start - generate new task_id
            task_id = checkpoint_mgr.generate_task_id(content, filename)
            chunk_summaries = []
            chunk_details = []
            total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            print(f"  🆕 Starting fresh summarization (task_id: {task_id})")


        # Step 3: Map phase - summarize each chunk (sequential for now)
        print("Map phase: Summarizing chunks...")

        for i, chunk in enumerate(chunks[start_chunk_idx:], start=start_chunk_idx):
            print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                # Calculate chunk summary length (aim for proportional distribution)
                chunk_summary_length = max(100, min(300, summary_length // len(chunks)))
                
                # Calculate max_tokens for chunk (Chinese chars need ~2x tokens)
                chunk_max_tokens = max(500, min(1000, chunk_summary_length * 2))
                
                response = await self.llm_client.generate(
                    prompt=get_chunk_summary_prompt(
                        chunk_text=chunk['text'],
                        chunk_id=chunk['chunk_id'],
                        total_chunks=chunk['total_chunks'],
                        chunk_summary_length=chunk_summary_length
                    ),
                    system_message=CHUNK_SUMMARY_SYSTEM,
                    temperature=0.5,
                    max_tokens=chunk_max_tokens
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

                # Save checkpoint after each chunk
                checkpoint_mgr.save_checkpoint(
                    task_id=task_id,
                    chunk_summaries=chunk_summaries,
                    chunk_details=chunk_details,
                    total_tokens=total_tokens,
                    total_chunks=len(chunks),
                    metadata={
                        "filename": filename,
                        "original_length": original_length,
                        "summary_length": summary_length
                    }
                )

                usage = response["usage"]
                print(f"  Chunk {i + 1} summarized ({len(summary)} chars) - Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})")
            except Exception as e:
                print(f"  Error summarizing chunk {i + 1}: {str(e)}")
                raise Exception(f"Failed to summarize chunk {i + 1}: {str(e)}")

        # Step 4: Reduce phase - generate final summary
        print("Reduce phase: Generating final summary...")
        try:
            summaries_text = "\n\n".join([
                f"片段 {i + 1} 摘要：\n{summary}"
                for i, summary in enumerate(chunk_summaries)
            ])

            # Calculate max_tokens for final summary (Chinese chars need ~2x tokens)
            final_max_tokens = max(1000, min(16000, summary_length * 2))
            
            response = await self.llm_client.generate(
                prompt=get_final_summary_prompt(
                    summaries_text=summaries_text,
                    original_length=original_length,
                    summary_length=summary_length
                ),
                system_message=FINAL_SUMMARY_SYSTEM,
                temperature=0.6,
                max_tokens=final_max_tokens
            )
            final_summary = response["text"].strip()

            # Add final summary tokens
            total_tokens["prompt_tokens"] += response["usage"]["prompt_tokens"]
            total_tokens["completion_tokens"] += response["usage"]["completion_tokens"]
            total_tokens["total_tokens"] += response["usage"]["total_tokens"]

            usage = response["usage"]
            print(f"Final summary generated ({len(final_summary)} chars) - Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})")
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

    async def summarize_webpage(self, url: str, summary_length: int = 500) -> Dict[str, Any]:
        """
        Summarize a webpage using Map-Reduce approach (async)

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

        # Step 3: Map phase - summarize each chunk (sequential for now)
        print("Map phase: Summarizing chunks...")

        # Initialize variables
        chunk_summaries = []
        chunk_details = []
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for i, chunk in enumerate(chunks):
            print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                # Calculate chunk summary length (aim for proportional distribution)
                chunk_summary_length = max(100, min(300, summary_length // len(chunks)))
                
                # Calculate max_tokens for chunk (Chinese chars need ~2x tokens)
                chunk_max_tokens = max(500, min(1000, chunk_summary_length * 2))
                
                response = await self.llm_client.generate(
                    prompt=get_chunk_summary_prompt(
                        chunk_text=chunk['text'],
                        chunk_id=chunk['chunk_id'],
                        total_chunks=chunk['total_chunks'],
                        chunk_summary_length=chunk_summary_length
                    ),
                    system_message=CHUNK_SUMMARY_SYSTEM,
                    temperature=0.5,
                    max_tokens=chunk_max_tokens
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

                usage = response["usage"]
                print(f"  Chunk {i + 1} summarized ({len(summary)} chars) - Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})")
            except Exception as e:
                raise Exception(f"Failed to summarize chunk {i + 1}: {str(e)}")

        # Step 4: Reduce phase - generate final summary
        print("Reduce phase: Generating final summary...")
        try:
            summaries_text = "\n\n".join([
                f"片段 {i + 1} 摘要：\n{summary}"
                for i, summary in enumerate(chunk_summaries)
            ])

            # Calculate max_tokens for final summary (Chinese chars need ~2x tokens)
            final_max_tokens = max(1000, min(16000, summary_length * 2))
            
            response = await self.llm_client.generate(
                prompt=get_final_summary_prompt(
                    summaries_text=summaries_text,
                    original_length=original_length,
                    summary_length=summary_length
                ),
                system_message=FINAL_SUMMARY_SYSTEM,
                temperature=0.6,
                max_tokens=final_max_tokens
            )
            final_summary = response["text"].strip()

            # Add final summary tokens
            total_tokens["prompt_tokens"] += response["usage"]["prompt_tokens"]
            total_tokens["completion_tokens"] += response["usage"]["completion_tokens"]
            total_tokens["total_tokens"] += response["usage"]["total_tokens"]
            
            usage = response["usage"]
            print(f"Final summary generated ({len(final_summary)} chars) - Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})")
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

    async def summarize_text(
        self,
        text: str,
        filename: str,
        summary_length: int = 500
    ) -> Dict[str, Any]:
        """
        Summarize raw text using Map-Reduce approach (async)

        This method is useful for summarizing transcribed audio/video text.

        Args:
            text: Raw text to summarize
            filename: Source filename (for metadata)
            summary_length: Target summary length in characters

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        original_length = len(text)
        print(f"Processing text: {original_length} characters")

        if not text.strip():
            raise ValueError("Text is empty")

        # Step 1: Chunk the text
        print("Chunking text...")
        chunks = self.chunker.create_chunks(text)
        print(f"Created {len(chunks)} chunks")

        if not chunks:
            raise ValueError("Failed to create chunks from text")

        # Step 2: Map phase - summarize each chunk
        print("Map phase: Summarizing chunks...")
        chunk_summaries = []
        chunk_details = []
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for i, chunk in enumerate(chunks):
            print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                # Calculate chunk summary length
                chunk_summary_length = max(100, min(300, summary_length // len(chunks)))
                chunk_max_tokens = max(500, min(1000, chunk_summary_length * 2))

                response = await self.llm_client.generate(
                    prompt=get_chunk_summary_prompt(
                        chunk_text=chunk['text'],
                        chunk_id=chunk['chunk_id'],
                        total_chunks=chunk['total_chunks'],
                        chunk_summary_length=chunk_summary_length
                    ),
                    system_message=CHUNK_SUMMARY_SYSTEM,
                    temperature=0.5,
                    max_tokens=chunk_max_tokens
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

                usage = response["usage"]
                print(f"  Chunk {i + 1} summarized ({len(summary)} chars) - Tokens: {usage['total_tokens']}")
            except Exception as e:
                print(f"  Error summarizing chunk {i + 1}: {str(e)}")
                raise Exception(f"Failed to summarize chunk {i + 1}: {str(e)}")

        # Step 3: Reduce phase - generate final summary
        print("Reduce phase: Generating final summary...")
        try:
            summaries_text = "\n\n".join([
                f"片段 {i + 1} 摘要：\n{summary}"
                for i, summary in enumerate(chunk_summaries)
            ])

            final_max_tokens = max(1000, min(16000, summary_length * 2))

            response = await self.llm_client.generate(
                prompt=get_final_summary_prompt(
                    summaries_text=summaries_text,
                    original_length=original_length,
                    summary_length=summary_length
                ),
                system_message=FINAL_SUMMARY_SYSTEM,
                temperature=0.6,
                max_tokens=final_max_tokens
            )
            final_summary = response["text"].strip()

            # Add final summary tokens
            total_tokens["prompt_tokens"] += response["usage"]["prompt_tokens"]
            total_tokens["completion_tokens"] += response["usage"]["completion_tokens"]
            total_tokens["total_tokens"] += response["usage"]["total_tokens"]

            usage = response["usage"]
            print(f"Final summary generated ({len(final_summary)} chars) - Tokens: {usage['total_tokens']}")
        except Exception as e:
            print(f"Error generating final summary: {str(e)}")
            raise Exception(f"Failed to generate final summary: {str(e)}")

        # Calculate processing time
        processing_time = time.time() - start_time

        return {
            'filename': filename,
            'original_length': original_length,
            'chunk_count': len(chunks),
            'num_chunks': len(chunks),
            'chunk_details': chunk_details,
            'chunk_summaries': chunk_summaries,
            'summary': final_summary,
            'final_summary': final_summary,
            'processing_time': round(processing_time, 2),
            'model': self.llm_client.model,
            'provider': self.llm_client.provider,
            'total_tokens': total_tokens['total_tokens'],
            'token_usage': total_tokens
        }


# Global summarizer instance
_summarizer: AsyncMapReduceSummarizer = None


def get_summarizer() -> AsyncMapReduceSummarizer:
    """Get or create global async summarizer instance"""
    global _summarizer
    if _summarizer is None:
        _summarizer = AsyncMapReduceSummarizer()
    return _summarizer
