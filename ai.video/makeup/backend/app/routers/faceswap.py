import os
import uuid
import aiofiles
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.models.schemas import (
    TaskResponse,
    UploadResponse,
    FaceSwapRequest,
    FaceSwapResponse,
    TaskStatus
)
from app.utils.storage import (
    create_task,
    get_task,
    get_all_tasks,
    update_task,
    get_upload_path,
    OUTPUTS_DIR
)
from app.services.faceswap_service import process_faceswap


router = APIRouter(prefix="/api", tags=["faceswap"])


# Allowed file extensions
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_file_type(filename: str) -> str:
    """Determine if file is video or image based on extension."""
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_VIDEO_EXTENSIONS:
        return "video"
    elif ext in ALLOWED_IMAGE_EXTENSIONS:
        return "image"
    else:
        raise ValueError(f"Unsupported file type: {ext}")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a video or face image file.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    try:
        file_type = get_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    filepath = get_upload_path(unique_filename)

    # Save file
    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    return UploadResponse(
        filename=file.filename,
        filepath=str(filepath),
        file_type=file_type
    )


@router.post("/faceswap", response_model=FaceSwapResponse)
async def start_faceswap(
    request: FaceSwapRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a face swap task.
    """
    # Validate file paths
    if not os.path.exists(request.source_face_path):
        raise HTTPException(
            status_code=400,
            detail=f"Source face image not found: {request.source_face_path}"
        )

    if not os.path.exists(request.target_video_path):
        raise HTTPException(
            status_code=400,
            detail=f"Target video not found: {request.target_video_path}"
        )

    # Create task
    task = create_task(
        source_face_path=request.source_face_path,
        target_video_path=request.target_video_path
    )

    # Start processing in background
    background_tasks.add_task(
        process_faceswap,
        task.task_id,
        request.source_face_path,
        request.target_video_path
    )

    return FaceSwapResponse(
        task_id=task.task_id,
        status=TaskStatus.PROCESSING,
        message="Face swap task started"
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a specific task.
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        output_path=task.output_path,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks():
    """
    Get all tasks.
    """
    tasks = get_all_tasks()
    return [
        TaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            output_path=task.output_path,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]


@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    Download the processed video.
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Task is not completed. Current status: {task.status}"
        )

    if not task.output_path or not os.path.exists(task.output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=task.output_path,
        filename=f"faceswap_{task_id}.mp4",
        media_type="video/mp4"
    )
