from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class ProcessingStatus(str, Enum):
    """Processing status enum"""
    PENDING = "pending"
    UPLOADING = "uploading"
    EXTRACTING_SUBTITLES = "extracting_subtitles"
    ANALYZING_CONTENT = "analyzing_content"
    SPLITTING_VIDEO = "splitting_video"
    COMPLETED = "completed"
    FAILED = "failed"


class ChapterInfo(BaseModel):
    """Chapter information"""
    chapter_id: str
    title: str
    start_time: float  # seconds
    end_time: float    # seconds
    duration: float    # seconds
    subtitle_text: str
    video_path: Optional[str] = None
    subtitle_path: Optional[str] = None


class VideoMetadata(BaseModel):
    """Video metadata"""
    video_id: str
    filename: str
    duration: float
    file_size: int
    upload_path: str
    created_at: str


class ProcessingTask(BaseModel):
    """Processing task status"""
    task_id: str
    video_id: str
    status: ProcessingStatus
    progress: float  # 0-100
    current_step: str
    error_message: Optional[str] = None
    video_metadata: Optional[VideoMetadata] = None
    chapters: List[ChapterInfo] = []


class VideoTreeNode(BaseModel):
    """Video tree node for parent-child relationship"""
    video_id: str
    title: str
    duration: float
    is_parent: bool
    video_path: str
    subtitle_path: Optional[str] = None
    children: List['VideoTreeNode'] = []


class UploadResponse(BaseModel):
    """Upload response"""
    task_id: str
    video_id: str
    message: str


class StatusResponse(BaseModel):
    """Status response"""
    task: ProcessingTask


class TreeResponse(BaseModel):
    """Tree response"""
    tree: VideoTreeNode
