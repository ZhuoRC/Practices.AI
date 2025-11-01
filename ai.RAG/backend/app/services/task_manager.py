from typing import Dict, Optional
from datetime import datetime
from enum import Enum
import threading


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskInfo:
    """Task information"""
    def __init__(self, task_id: str, task_type: str, filename: str):
        self.task_id = task_id
        self.task_type = task_type
        self.filename = filename
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.message = "Task queued"
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.result: Optional[Dict] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "filename": self.filename,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error
        }


class TaskManager:
    """Manager for background tasks"""

    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self._lock = threading.Lock()

    def create_task(self, task_id: str, task_type: str, filename: str) -> TaskInfo:
        """Create a new task"""
        with self._lock:
            task = TaskInfo(task_id, task_type, filename)
            self.tasks[task_id] = task
            return task

    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update task information"""
        with self._lock:
            if task_id not in self.tasks:
                return

            task = self.tasks[task_id]
            if status is not None:
                task.status = status
            if progress is not None:
                task.progress = progress
            if message is not None:
                task.message = message
            if result is not None:
                task.result = result
            if error is not None:
                task.error = error
            task.updated_at = datetime.now().isoformat()

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information"""
        with self._lock:
            return self.tasks.get(task_id)

    def delete_task(self, task_id: str):
        """Delete a task"""
        with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]

    def list_tasks(self) -> list:
        """List all tasks"""
        with self._lock:
            return [task.to_dict() for task in self.tasks.values()]

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks"""
        with self._lock:
            current_time = datetime.now()
            tasks_to_delete = []

            for task_id, task in self.tasks.items():
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task_time = datetime.fromisoformat(task.updated_at)
                    age_hours = (current_time - task_time).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        tasks_to_delete.append(task_id)

            for task_id in tasks_to_delete:
                del self.tasks[task_id]

            return len(tasks_to_delete)


# Global instance
task_manager = TaskManager()
