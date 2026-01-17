from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import uuid
import shutil
from pathlib import Path
import asyncio
import logging
import os

from ..models import UploadResponse, StatusResponse, TreeResponse, VideoTreeNode
from ..config import settings
from ..services.task_manager import get_task_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["video"])


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file for processing
    
    Args:
        file: Video file
        
    Returns:
        Upload response with task_id and video_id
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_extension = Path(file.filename).suffix
        upload_filename = f"{video_id}{file_extension}"
        upload_path = settings.upload_path / upload_filename
        
        # Save file
        with open(upload_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = upload_path.stat().st_size
        
        logger.info(f"Uploaded video {video_id}: {file.filename} ({file_size} bytes)")
        
        # Create processing task
        task_manager = get_task_manager()
        task_id = task_manager.create_task(
            video_id,
            str(upload_path),
            file.filename,
            file_size
        )
        
        # Start processing in background
        asyncio.create_task(task_manager.process_video(task_id))
        
        return UploadResponse(
            task_id=task_id,
            video_id=video_id,
            message="Video uploaded successfully. Processing started."
        )
        
    except Exception as e:
        logger.error(f"Error uploading video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    """
    Get processing status for a task
    
    Args:
        task_id: Task ID
        
    Returns:
        Status response
    """
    try:
        task_manager = get_task_manager()
        task = task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found. The server may have been restarted.")
        
        return StatusResponse(task=task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/tree/{video_id}", response_model=TreeResponse)
async def get_video_tree(video_id: str):
    """
    Get video tree structure (parent and children)
    
    Args:
        video_id: Video ID
        
    Returns:
        Tree response
    """
    task_manager = get_task_manager()
    
    # Find task by video_id
    task = None
    for t in task_manager.tasks.values():
        if t.video_id == video_id:
            task = t
            break
    
    if not task or not task.video_metadata:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Build tree structure
    parent_node = VideoTreeNode(
        video_id=video_id,
        title=task.video_metadata.filename,
        duration=task.video_metadata.duration,
        is_parent=True,
        video_path=task.video_metadata.upload_path,
        subtitle_path=str(settings.processed_path / f"{video_id}_full.srt"),
        children=[]
    )
    
    # Add children
    for chapter in task.chapters:
        child_node = VideoTreeNode(
            video_id=chapter.chapter_id,
            title=chapter.title,
            duration=chapter.duration,
            is_parent=False,
            video_path=chapter.video_path,
            subtitle_path=chapter.subtitle_path,
            children=[]
        )
        parent_node.children.append(child_node)
    
    return TreeResponse(tree=parent_node)


@router.get("/preview/{video_id}")
async def preview_video(video_id: str):
    """
    Stream video for preview
    
    Args:
        video_id: Video ID or chapter ID
        
    Returns:
        Video file stream
    """
    # Try to find video file
    video_path = None
    
    # Check if it's a parent video
    task_manager = get_task_manager()
    for task in task_manager.tasks.values():
        if task.video_id == video_id:
            video_path = task.video_metadata.upload_path
            break
        
        # Check if it's a chapter
        for chapter in task.chapters:
            if chapter.chapter_id == video_id:
                video_path = chapter.video_path
                break
    
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=Path(video_path).name
    )


@router.get("/subtitle/{video_id}")
async def get_subtitle(video_id: str):
    """
    Get subtitle content
    
    Args:
        video_id: Video ID or chapter ID
        
    Returns:
        Subtitle text content
    """
    # Try to find subtitle file
    subtitle_path = None
    
    task_manager = get_task_manager()
    for task in task_manager.tasks.values():
        if task.video_id == video_id:
            subtitle_path = str(settings.processed_path / f"{video_id}_full.srt")
            break
        
        # Check if it's a chapter
        for chapter in task.chapters:
            if chapter.chapter_id == video_id:
                subtitle_path = chapter.subtitle_path
                break
    
    if not subtitle_path or not Path(subtitle_path).exists():
        raise HTTPException(status_code=404, detail="Subtitle not found")
    
    # Read subtitle content
    with open(subtitle_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {"subtitle": content}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    llm_model = settings.qwen_model if settings.llm_provider == "qwen" else settings.ollama_model
    return {
        "status": "healthy",
        "whisper_model": settings.whisper_model,
        "llm_provider": settings.llm_provider,
        "llm_model": llm_model
    }
