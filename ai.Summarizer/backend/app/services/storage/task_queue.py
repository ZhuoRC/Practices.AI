"""
Task queue service for async document processing.
Handles background tasks and status tracking.
"""
import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """Task result data structure."""
    task_id: str
    status: TaskStatus
    created_at: str
    updated_at: str
    filename: str
    file_size: int

    # Optional fields
    progress: Optional[str] = None
    progress_percent: Optional[int] = None  # Progress percentage (0-100)
    error: Optional[str] = None

    # Result fields (populated on completion)
    summary: Optional[str] = None
    chunk_count: Optional[int] = None
    total_tokens: Optional[int] = None
    processing_time: Optional[float] = None
    transcription_duration: Optional[float] = None
    transcription_text_length: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TaskQueue:
    """
    In-memory task queue for async processing.
    For production, consider using Redis or a proper queue system.
    """

    def __init__(self):
        """Initialize task queue."""
        self._tasks: Dict[str, TaskResult] = {}
        self._lock = asyncio.Lock()
        logger.info("TaskQueue initialized")

    def generate_task_id(self) -> str:
        """Generate unique task ID."""
        return str(uuid.uuid4())

    async def create_task(
        self,
        filename: str,
        file_size: int
    ) -> str:
        """
        Create a new task.

        Args:
            filename: Original filename
            file_size: File size in bytes

        Returns:
            Task ID
        """
        task_id = self.generate_task_id()
        now = datetime.utcnow().isoformat()

        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            filename=filename,
            file_size=file_size,
            progress="Task created, waiting to process"
        )

        async with self._lock:
            self._tasks[task_id] = task_result

        logger.info(f"Task created: {task_id} for file: {filename}")
        return task_id

    async def get_task(self, task_id: str) -> Optional[TaskResult]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            TaskResult or None if not found
        """
        async with self._lock:
            return self._tasks.get(task_id)

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: Optional[str] = None,
        progress_percent: Optional[int] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Update task status.

        Args:
            task_id: Task ID
            status: New status
            progress: Optional progress message
            progress_percent: Optional progress percentage (0-100)
            error: Optional error message
        """
        async with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = status
                task.updated_at = datetime.utcnow().isoformat()

                if progress is not None:
                    task.progress = progress
                if progress_percent is not None:
                    task.progress_percent = progress_percent
                if error is not None:
                    task.error = error

                logger.info(
                    f"Task {task_id} updated: status={status}, progress={progress}"
                )

    async def update_task_result(
        self,
        task_id: str,
        summary: str,
        chunk_count: int,
        total_tokens: int,
        processing_time: float,
        transcription_duration: Optional[float] = None,
        transcription_text_length: Optional[int] = None
    ) -> None:
        """
        Update task with completion results.

        Args:
            task_id: Task ID
            summary: Generated summary
            chunk_count: Number of chunks processed
            total_tokens: Total tokens used
            processing_time: Total processing time in seconds
            transcription_duration: Audio duration in seconds
            transcription_text_length: Length of transcribed text
        """
        async with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.updated_at = datetime.utcnow().isoformat()
                task.summary = summary
                task.chunk_count = chunk_count
                task.total_tokens = total_tokens
                task.processing_time = processing_time
                task.transcription_duration = transcription_duration
                task.transcription_text_length = transcription_text_length
                task.progress = "Processing completed successfully"

                logger.info(
                    f"Task {task_id} completed: {chunk_count} chunks, "
                    f"{total_tokens} tokens, {processing_time:.2f}s"
                )

    async def mark_task_failed(
        self,
        task_id: str,
        error: str
    ) -> None:
        """
        Mark task as failed.

        Args:
            task_id: Task ID
            error: Error message
        """
        async with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.updated_at = datetime.utcnow().isoformat()
                task.error = error
                task.progress = "Processing failed"

                logger.error(f"Task {task_id} failed: {error}")

    async def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed/failed tasks.

        Args:
            max_age_hours: Maximum age of tasks to keep

        Returns:
            Number of tasks removed
        """
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed_count = 0

        async with self._lock:
            tasks_to_remove = []

            for task_id, task in self._tasks.items():
                task_time = datetime.fromisoformat(task.updated_at)
                if task_time < cutoff_time and task.status in [
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED
                ]:
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self._tasks[task_id]
                removed_count += 1

        logger.info(f"Cleaned up {removed_count} old tasks")
        return removed_count

    async def get_all_tasks(self) -> Dict[str, TaskResult]:
        """Get all tasks."""
        async with self._lock:
            return self._tasks.copy()


# Global task queue instance
task_queue = TaskQueue()
