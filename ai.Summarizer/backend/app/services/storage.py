"""Summary storage service"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..config import settings


class SummaryStorage:
    """Service for storing and retrieving summary history"""

    def __init__(self, storage_dir: str = None):
        """
        Initialize storage service

        Args:
            storage_dir: Directory to store summaries. Defaults to data/summaries
        """
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(settings.document_storage_path),
                "summaries"
            )

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Index file to track all summaries
        self.index_file = self.storage_dir / "index.json"
        self._ensure_index()

    def _ensure_index(self):
        """Ensure index file exists"""
        if not self.index_file.exists():
            self._write_index([])

    def _read_index(self) -> List[Dict[str, Any]]:
        """Read summary index"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _write_index(self, index: List[Dict[str, Any]]):
        """Write summary index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def save_summary(
        self,
        summary_data: Dict[str, Any],
        source_type: str,
        source_name: str
    ) -> str:
        """
        Save a summary to storage

        Args:
            summary_data: Complete summary data from summarizer
            source_type: 'document' or 'webpage'
            source_name: Filename or URL

        Returns:
            Summary ID (filename without extension)
        """
        # Generate unique ID based on timestamp
        timestamp = datetime.now()
        summary_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")

        # Prepare metadata
        metadata = {
            "id": summary_id,
            "timestamp": timestamp.isoformat(),
            "source_type": source_type,
            "source_name": source_name,
            "num_chunks": summary_data.get("num_chunks", 0),
            "processing_time": summary_data.get("processing_time", 0),
            "model": summary_data.get("model", "unknown"),
            "provider": summary_data.get("provider", "unknown"),
            "token_usage": summary_data.get("token_usage", {}),
            "original_length": summary_data.get("original_length", 0)
        }

        # Save full summary data
        summary_file = self.storage_dir / f"{summary_id}.json"
        full_data = {
            "metadata": metadata,
            "summary": summary_data.get("final_summary", ""),
            "chunk_summaries": summary_data.get("chunk_summaries", []),
            "chunk_details": summary_data.get("chunk_details", [])
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)

        # Update index
        index = self._read_index()
        index.insert(0, metadata)  # Add to beginning (newest first)

        # Keep only last 100 summaries in index
        if len(index) > 100:
            # Delete old summary files
            for old_item in index[100:]:
                old_file = self.storage_dir / f"{old_item['id']}.json"
                if old_file.exists():
                    old_file.unlink()
            index = index[:100]

        self._write_index(index)

        print(f"Summary saved: {summary_id}")
        return summary_id

    def get_summary(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a summary by ID

        Args:
            summary_id: Summary ID

        Returns:
            Summary data or None if not found
        """
        summary_file = self.storage_dir / f"{summary_id}.json"
        if not summary_file.exists():
            return None

        with open(summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_summaries(
        self,
        limit: int = 20,
        offset: int = 0,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List summaries with pagination

        Args:
            limit: Maximum number of summaries to return
            offset: Number of summaries to skip
            source_type: Filter by source type ('document' or 'webpage')

        Returns:
            List of summary metadata
        """
        index = self._read_index()

        # Filter by source type if specified
        if source_type:
            index = [item for item in index if item.get("source_type") == source_type]

        # Apply pagination
        return index[offset:offset + limit]

    def delete_summary(self, summary_id: str) -> bool:
        """
        Delete a summary

        Args:
            summary_id: Summary ID

        Returns:
            True if deleted, False if not found
        """
        summary_file = self.storage_dir / f"{summary_id}.json"
        if not summary_file.exists():
            return False

        # Remove from index
        index = self._read_index()
        index = [item for item in index if item.get("id") != summary_id]
        self._write_index(index)

        # Delete file
        summary_file.unlink()
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics

        Returns:
            Statistics about stored summaries
        """
        index = self._read_index()

        total_count = len(index)
        document_count = sum(1 for item in index if item.get("source_type") == "document")
        webpage_count = sum(1 for item in index if item.get("source_type") == "webpage")

        total_tokens = sum(
            item.get("token_usage", {}).get("total_tokens", 0)
            for item in index
        )

        total_processing_time = sum(
            item.get("processing_time", 0)
            for item in index
        )

        return {
            "total_summaries": total_count,
            "document_summaries": document_count,
            "webpage_summaries": webpage_count,
            "total_tokens_used": total_tokens,
            "total_processing_time": round(total_processing_time, 2),
            "storage_directory": str(self.storage_dir)
        }


# Global storage instance
_storage: Optional[SummaryStorage] = None


def get_storage() -> SummaryStorage:
    """Get or create global storage instance"""
    global _storage
    if _storage is None:
        _storage = SummaryStorage()
    return _storage
