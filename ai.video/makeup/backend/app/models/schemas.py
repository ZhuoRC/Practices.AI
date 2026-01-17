from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskCreate(BaseModel):
    source_face_path: str
    target_video_path: str


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int = 0
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class TaskInDB(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int = 0
    source_face_path: str
    target_video_path: str
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class UploadResponse(BaseModel):
    filename: str
    filepath: str
    file_type: str  # "video" or "image"


class FaceSwapRequest(BaseModel):
    task_id: str
    source_face_path: str
    target_video_path: str


class FaceSwapResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str
