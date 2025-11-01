"""Checkpoint manager for resumable summarization"""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class CheckpointManager:
    """Manage checkpoints for resumable summarization"""

    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def generate_task_id(self, content: bytes, source_name: str) -> str:
        """Generate unique task ID based on content hash"""
        content_hash = hashlib.md5(content).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use content hash to ensure same file resumes from same checkpoint
        return f"{content_hash}_{timestamp}"

    def get_checkpoint_path(self, task_id: str) -> Path:
        """Get checkpoint file path"""
        return self.checkpoint_dir / f"{task_id}.json"

    def save_checkpoint(
        self,
        task_id: str,
        chunk_summaries: List[str],
        chunk_details: List[Dict[str, Any]],
        total_tokens: Dict[str, int],
        total_chunks: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save checkpoint"""
        checkpoint_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "progress": {
                "completed_chunks": len(chunk_summaries),
                "total_chunks": total_chunks,
                "percentage": round(len(chunk_summaries) / total_chunks * 100, 2)
            },
            "chunk_summaries": chunk_summaries,
            "chunk_details": chunk_details,
            "total_tokens": total_tokens,
            "metadata": metadata or {}
        }

        checkpoint_path = self.get_checkpoint_path(task_id)
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        print(f"  💾 Checkpoint saved: {len(chunk_summaries)}/{total_chunks} chunks completed")

    def load_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint if exists"""
        checkpoint_path = self.get_checkpoint_path(task_id)

        if not checkpoint_path.exists():
            return None

        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)

            print(f"  ✓ Found checkpoint: {checkpoint_data['progress']['completed_chunks']}/{checkpoint_data['progress']['total_chunks']} chunks already completed")
            print(f"  ⏭ Resuming from chunk {checkpoint_data['progress']['completed_chunks'] + 1}")

            return checkpoint_data
        except Exception as e:
            print(f"  ⚠ Failed to load checkpoint: {str(e)}")
            return None

    def find_checkpoint_by_content(self, content: bytes) -> Optional[str]:
        """Find existing checkpoint by content hash"""
        content_hash = hashlib.md5(content).hexdigest()[:12]

        # Look for checkpoints with matching content hash
        for checkpoint_file in self.checkpoint_dir.glob(f"{content_hash}_*.json"):
            return checkpoint_file.stem  # Return task_id

        return None

    def delete_checkpoint(self, task_id: str):
        """Delete checkpoint after successful completion"""
        checkpoint_path = self.get_checkpoint_path(task_id)

        if checkpoint_path.exists():
            checkpoint_path.unlink()
            print(f"  🗑 Checkpoint cleaned up: {task_id}")

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all checkpoints"""
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    checkpoints.append({
                        "task_id": data["task_id"],
                        "timestamp": data["timestamp"],
                        "progress": data["progress"],
                        "metadata": data.get("metadata", {})
                    })
            except Exception as e:
                print(f"  ⚠ Failed to read checkpoint {checkpoint_file.name}: {str(e)}")

        return checkpoints

    def cleanup_old_checkpoints(self, days: int = 7):
        """Clean up checkpoints older than specified days"""
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(days=days)
        cleaned = 0

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    checkpoint_time = datetime.fromisoformat(data["timestamp"])

                    if checkpoint_time < cutoff_time:
                        checkpoint_file.unlink()
                        cleaned += 1
            except Exception as e:
                print(f"  ⚠ Failed to process {checkpoint_file.name}: {str(e)}")

        if cleaned > 0:
            print(f"  🗑 Cleaned up {cleaned} old checkpoint(s)")

        return cleaned


# Global checkpoint manager instance
_checkpoint_manager: CheckpointManager = None


def get_checkpoint_manager() -> CheckpointManager:
    """Get or create global checkpoint manager instance"""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
