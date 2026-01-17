import json
import os
from typing import List, Optional
from datetime import datetime
import uuid
from pathlib import Path

from app.models.schemas import TaskInDB, TaskStatus


# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"


def ensure_directories():
    """Ensure all required directories exist."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]")


def load_tasks() -> List[dict]:
    """Load all tasks from JSON file."""
    ensure_directories()
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_tasks(tasks: List[dict]):
    """Save all tasks to JSON file."""
    ensure_directories()
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def create_task(source_face_path: str, target_video_path: str) -> TaskInDB:
    """Create a new task."""
    tasks = load_tasks()
    now = datetime.now().isoformat()

    task = TaskInDB(
        task_id=str(uuid.uuid4()),
        status=TaskStatus.PENDING,
        progress=0,
        source_face_path=source_face_path,
        target_video_path=target_video_path,
        output_path=None,
        error_message=None,
        created_at=now,
        updated_at=now
    )

    tasks.append(task.model_dump())
    save_tasks(tasks)
    return task


def get_task(task_id: str) -> Optional[TaskInDB]:
    """Get a task by ID."""
    tasks = load_tasks()
    for task in tasks:
        if task["task_id"] == task_id:
            return TaskInDB(**task)
    return None


def get_all_tasks() -> List[TaskInDB]:
    """Get all tasks."""
    tasks = load_tasks()
    return [TaskInDB(**task) for task in tasks]


def update_task(
    task_id: str,
    status: Optional[TaskStatus] = None,
    progress: Optional[int] = None,
    output_path: Optional[str] = None,
    error_message: Optional[str] = None
) -> Optional[TaskInDB]:
    """Update a task."""
    tasks = load_tasks()

    for i, task in enumerate(tasks):
        if task["task_id"] == task_id:
            if status is not None:
                task["status"] = status.value
            if progress is not None:
                task["progress"] = progress
            if output_path is not None:
                task["output_path"] = output_path
            if error_message is not None:
                task["error_message"] = error_message
            task["updated_at"] = datetime.now().isoformat()

            tasks[i] = task
            save_tasks(tasks)
            return TaskInDB(**task)

    return None


def delete_task(task_id: str) -> bool:
    """Delete a task by ID."""
    tasks = load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t["task_id"] != task_id]

    if len(tasks) < original_len:
        save_tasks(tasks)
        return True
    return False


def get_upload_path(filename: str) -> Path:
    """Get the full path for an uploaded file."""
    ensure_directories()
    return UPLOADS_DIR / filename


def get_output_path(filename: str) -> Path:
    """Get the full path for an output file."""
    ensure_directories()
    return OUTPUTS_DIR / filename
