import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import logging

from ..models import ProcessingTask, ProcessingStatus, VideoMetadata, ChapterInfo
from ..config import settings
from .whisper_service import get_whisper_service
from .llm_service import LLMService
from .video_service import VideoService

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages background video processing tasks"""
    
    def __init__(self):
        """Initialize task manager"""
        self.tasks: Dict[str, ProcessingTask] = {}
        self.video_service = VideoService(settings.processed_path, settings.temp_path)
        
        # Initialize LLM service based on provider
        if settings.llm_provider == "qwen":
            self.llm_service = LLMService(
                provider="qwen",
                api_key=settings.qwen_api_key,
                api_base=settings.qwen_api_base,
                model=settings.qwen_model
            )
        else:  # ollama
            self.llm_service = LLMService(
                provider="ollama",
                api_key="",
                api_base=settings.ollama_base_url,
                model=settings.ollama_model
            )
        
        logger.info("TaskManager initialized")
    
    def create_task(self, video_id: str, video_path: str, filename: str, file_size: int) -> str:
        """
        Create a new processing task
        
        Args:
            video_id: Unique video ID
            video_path: Path to uploaded video
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        # Get video duration
        duration = self.video_service.get_video_duration(video_path)
        
        # Create video metadata
        video_metadata = VideoMetadata(
            video_id=video_id,
            filename=filename,
            duration=duration,
            file_size=file_size,
            upload_path=video_path,
            created_at=datetime.now().isoformat()
        )
        
        # Create task
        task = ProcessingTask(
            task_id=task_id,
            video_id=video_id,
            status=ProcessingStatus.PENDING,
            progress=0.0,
            current_step="Task created",
            video_metadata=video_metadata,
            chapters=[]
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id} for video {video_id}")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def update_task_status(
        self,
        task_id: str,
        status: ProcessingStatus,
        progress: float,
        current_step: str,
        error_message: Optional[str] = None
    ):
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].progress = progress
            self.tasks[task_id].current_step = current_step
            if error_message:
                self.tasks[task_id].error_message = error_message
            logger.info(f"Task {task_id}: {status.value} - {progress}% - {current_step}")
    
    async def process_video(self, task_id: str):
        """
        Process video asynchronously
        
        Args:
            task_id: Task ID to process
        """
        try:
            task = self.tasks[task_id]
            video_path = task.video_metadata.upload_path
            video_id = task.video_id
            
            # Step 1: Extract subtitles with Whisper
            self.update_task_status(
                task_id,
                ProcessingStatus.EXTRACTING_SUBTITLES,
                10.0,
                "Extracting subtitles with Whisper..."
            )
            
            whisper_service = get_whisper_service(settings.whisper_model)
            result = await asyncio.to_thread(whisper_service.extract_subtitles, video_path)
            
            # Save full subtitle file
            full_subtitle_path = settings.processed_path / f"{video_id}_full.srt"
            whisper_service.format_as_srt(result, str(full_subtitle_path))
            
            segments = whisper_service.get_segments_with_timestamps(result)
            
            self.update_task_status(
                task_id,
                ProcessingStatus.EXTRACTING_SUBTITLES,
                40.0,
                f"Extracted {len(segments)} subtitle segments"
            )
            
            # Step 2: Segment into chapters with LLM
            self.update_task_status(
                task_id,
                ProcessingStatus.ANALYZING_CONTENT,
                45.0,
                "Analyzing content with LLM..."
            )
            
            chapters = await asyncio.to_thread(
                self.llm_service.segment_into_chapters,
                segments,
                settings.target_chapter_duration,
                settings.min_chapter_duration,
                settings.max_chapter_duration
            )
            
            self.update_task_status(
                task_id,
                ProcessingStatus.ANALYZING_CONTENT,
                60.0,
                f"Created {len(chapters)} chapters"
            )
            
            # Step 3: Split video into chapters
            self.update_task_status(
                task_id,
                ProcessingStatus.SPLITTING_VIDEO,
                65.0,
                "Splitting video into chapters..."
            )
            
            # Split videos
            split_chapters = await asyncio.to_thread(
                self.video_service.split_video,
                video_path,
                chapters,
                video_id
            )
            
            # Create subtitle files for each chapter
            chapter_infos = []
            for i, chapter in enumerate(split_chapters):
                # Create subtitle file
                subtitle_path = self.video_service.create_subtitle_file(
                    chapter,
                    video_id,
                    i
                )
                
                # Create ChapterInfo
                chapter_info = ChapterInfo(
                    chapter_id=chapter['chapter_id'],
                    title=chapter['title'],
                    start_time=chapter['start_time'],
                    end_time=chapter['end_time'],
                    duration=chapter['duration'],
                    subtitle_text=chapter['subtitle_text'],
                    video_path=chapter['video_path'],
                    subtitle_path=subtitle_path
                )
                chapter_infos.append(chapter_info)
                
                # Update progress
                progress = 65.0 + (30.0 * (i + 1) / len(split_chapters))
                self.update_task_status(
                    task_id,
                    ProcessingStatus.SPLITTING_VIDEO,
                    progress,
                    f"Processing chapter {i+1}/{len(split_chapters)}"
                )
            
            # Update task with chapters
            self.tasks[task_id].chapters = chapter_infos
            
            # Complete
            self.update_task_status(
                task_id,
                ProcessingStatus.COMPLETED,
                100.0,
                f"Completed! Created {len(chapter_infos)} chapters"
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}", exc_info=True)
            self.update_task_status(
                task_id,
                ProcessingStatus.FAILED,
                0.0,
                "Processing failed",
                error_message=str(e)
            )


# Global task manager instance
_task_manager = None


def get_task_manager() -> TaskManager:
    """Get or create TaskManager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
