"""API endpoints for document summarization"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional
from pathlib import Path
import shutil
import asyncio
import time
from ..services import get_summarizer, get_storage, task_queue, TaskStatus, AudioVideoLoader, TranscriptionManager
from ..config import settings

router = APIRouter(prefix="/api/summarize", tags=["summarize"])


class WebpageSummarizeRequest(BaseModel):
    """Request model for webpage summarization"""
    url: HttpUrl
    summary_length: Optional[int] = 500  # Target summary length in characters


class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/document", response_model=SummarizeResponse)
async def summarize_document(
    file: UploadFile = File(..., description="Document file to summarize (PDF, TXT, DOCX)"),
    summary_length: int = Form(500, description="Target summary length in characters")
):
    """
    Summarize a document using Map-Reduce approach

    - **file**: Document file (PDF, TXT, DOCX)

    Returns the final summary along with chunk summaries and metadata
    """
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        allowed_extensions = [
            '.pdf', '.txt', '.docx', '.doc', '.md', '.text',  # Documents
            '.mp3', '.wav', '.m4a',  # Audio
            '.mp4', '.avi', '.mov', '.mkv'  # Video
        ]

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Get summarizer and process (async)
        summarizer = get_summarizer()
        result = await summarizer.summarize_document(
            content=content,
            file_type=file_extension,
            filename=file.filename,
            summary_length=summary_length
        )

        # Save summary to storage
        storage = get_storage()
        summary_id = storage.save_summary(
            summary_data=result,
            source_type="document",
            source_name=file.filename
        )

        # Add summary_id to result
        result["summary_id"] = summary_id

        return SummarizeResponse(
            success=True,
            message="Document summarized successfully",
            data=result
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/webpage", response_model=SummarizeResponse)
async def summarize_webpage(request: WebpageSummarizeRequest):
    """
    Summarize a webpage using Map-Reduce approach

    - **url**: Webpage URL to summarize

    Returns the final summary along with chunk summaries and metadata
    """
    try:
        # Get summarizer and process (async)
        summarizer = get_summarizer()
        result = await summarizer.summarize_webpage(url=str(request.url), summary_length=request.summary_length)

        # Save summary to storage
        storage = get_storage()
        summary_id = storage.save_summary(
            summary_data=result,
            source_type="webpage",
            source_name=str(request.url)
        )

        # Add summary_id to result
        result["summary_id"] = summary_id

        return SummarizeResponse(
            success=True,
            message="Webpage summarized successfully",
            data=result
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        summarizer = get_summarizer()
        return {
            "status": "healthy",
            "llm_provider": summarizer.llm_client.provider,
            "llm_model": summarizer.llm_client.model,
            "chunker_config": {
                "min_size": settings.min_chunk_size,
                "max_size": settings.max_chunk_size,
                "overlap": settings.chunk_overlap
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/history")
async def get_history(
    limit: int = 20,
    offset: int = 0,
    source_type: Optional[str] = None
):
    """
    Get summary history

    - **limit**: Maximum number of summaries to return (default: 20)
    - **offset**: Number of summaries to skip (default: 0)
    - **source_type**: Filter by source type ('document' or 'webpage')
    """
    try:
        storage = get_storage()
        summaries = storage.list_summaries(limit=limit, offset=offset, source_type=source_type)
        return {
            "success": True,
            "count": len(summaries),
            "summaries": summaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/history/{summary_id}")
async def get_summary_by_id(summary_id: str):
    """
    Get a specific summary by ID

    - **summary_id**: Summary ID
    """
    try:
        storage = get_storage()
        summary = storage.get_summary(summary_id)
        
        if summary is None:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return {
            "success": True,
            "data": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.delete("/history/{summary_id}")
async def delete_summary(summary_id: str):
    """
    Delete a summary by ID

    - **summary_id**: Summary ID
    """
    try:
        storage = get_storage()
        deleted = storage.delete_summary(summary_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return {
            "success": True,
            "message": "Summary deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete summary: {str(e)}")


@router.get("/statistics")
async def get_statistics():
    """Get storage statistics"""
    try:
        storage = get_storage()
        stats = storage.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


async def process_document_background(
    task_id: str,
    content: bytes,
    filename: str,
    file_extension: str,
    summary_length: int
):
    """
    Background task to process document (especially audio/video).

    Args:
        task_id: Task ID for tracking
        content: File content bytes
        filename: Original filename
        file_extension: File extension
        summary_length: Target summary length
    """
    start_time = time.time()

    try:
        # Update task status to processing
        await task_queue.update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            progress="Processing file...",
            progress_percent=10
        )

        # Check if it's an audio/video file
        is_audio_video = AudioVideoLoader.is_audio_file(filename) or AudioVideoLoader.is_video_file(filename)

        if is_audio_video:
            # Process audio/video file
            await task_queue.update_task_status(
                task_id,
                TaskStatus.PROCESSING,
                progress="Transcribing audio...",
                progress_percent=30
            )

            # Prepare audio for transcription (extract from video if needed)
            audio_bytes, audio_ext = AudioVideoLoader.prepare_audio_for_transcription(
                content, filename
            )

            # Transcribe audio using transcription manager
            transcription_manager = TranscriptionManager()
            # Transcribe audio with progress callback
            async def transcription_progress_callback(message: str, percent: int):
                await task_queue.update_task_status(
                    task_id,
                    TaskStatus.PROCESSING,
                    progress=message,
                    progress_percent=percent
                )

            transcription_result = await transcription_manager.transcribe_async(
                audio_bytes, language=None, file_extension=audio_ext, progress_callback=transcription_progress_callback
            )

            # Use transcribed text as document content
            text_content = transcription_result["text"]
            transcription_duration = transcription_result["duration"]

            await task_queue.update_task_status(
                task_id,
                TaskStatus.PROCESSING,
                progress=f"Transcription complete ({len(text_content)} chars). Summarizing...",
                progress_percent=70
            )

            # Summarize transcribed text
            summarizer = get_summarizer()
            result = await summarizer.summarize_text(
                text=text_content,
                filename=filename,
                summary_length=summary_length
            )

            # Add transcription info to result
            result["transcription_duration"] = transcription_duration
            result["transcription_text_length"] = len(text_content)
            result["file_type"] = "audio/video"

        else:
            # Process regular document
            await task_queue.update_task_status(
                task_id,
                TaskStatus.PROCESSING,
                progress="Extracting text from document...",
                progress_percent=20
            )

            summarizer = get_summarizer()
            result = await summarizer.summarize_document(
                content=content,
                file_type=file_extension,
                filename=filename,
                summary_length=summary_length
            )
            result["file_type"] = "document"
            transcription_duration = None

        # Save summary to storage
        storage = get_storage()
        summary_id = storage.save_summary(
            summary_data=result,
            source_type="document",
            source_name=filename
        )

        result["summary_id"] = summary_id

        # Calculate processing time
        processing_time = time.time() - start_time

        # Update task with results
        await task_queue.update_task_result(
            task_id=task_id,
            summary=result["summary"],
            chunk_count=result.get("chunk_count", 0),
            total_tokens=result.get("total_tokens", 0),
            processing_time=processing_time,
            transcription_duration=transcription_duration,
            transcription_text_length=result.get("transcription_text_length")
        )

    except Exception as e:
        # Mark task as failed
        await task_queue.mark_task_failed(task_id, str(e))


@router.post("/document/async")
async def summarize_document_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document/Audio/Video file to summarize"),
    summary_length: int = Form(500, description="Target summary length in characters")
):
    """
    Asynchronously summarize a document/audio/video file.
    Returns a task_id for status polling.

    Recommended for audio/video files which require transcription.

    - **file**: Document/Audio/Video file
    - **summary_length**: Target summary length in characters

    Returns task_id for polling status via GET /task/{task_id}
    """
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        allowed_extensions = [
            '.pdf', '.txt', '.docx', '.doc', '.md', '.text',  # Documents
            '.mp3', '.wav', '.m4a',  # Audio
            '.mp4', '.avi', '.mov', '.mkv'  # Video
        ]

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Validate file size
        file_size = len(content)
        if file_size > settings.max_audio_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1_000_000:.2f} MB) exceeds maximum allowed size ({settings.max_audio_file_size / 1_000_000:.2f} MB)"
            )

        # Create task
        task_id = await task_queue.create_task(
            filename=file.filename,
            file_size=file_size
        )

        # Start background processing
        background_tasks.add_task(
            process_document_background,
            task_id=task_id,
            content=content,
            filename=file.filename,
            file_extension=file_extension,
            summary_length=summary_length
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": "Processing started. Use the task_id to poll for status.",
            "poll_endpoint": f"/api/summarize/task/{task_id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of an async processing task.

    - **task_id**: Task ID returned from /document/async

    Returns task status and results (if completed)
    """
    try:
        task = await task_queue.get_task(task_id)

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        return {
            "success": True,
            "task": task.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


async def transcribe_audio_background(
    task_id: str,
    content: bytes,
    filename: str,
    file_extension: str,
    language: Optional[str] = None
):
    """
    Background task to transcribe audio/video (no summarization).

    Args:
        task_id: Task ID for tracking
        content: File content bytes
        filename: Original filename
        file_extension: File extension
        language: Optional language code (e.g., 'zh', 'en', 'ja') for better accuracy
    """
    start_time = time.time()

    try:
        # Update task status to processing
        await task_queue.update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            progress="Preparing audio for transcription...",
            progress_percent=10
        )

        # Check if it's an audio/video file
        is_audio_video = AudioVideoLoader.is_audio_file(filename) or AudioVideoLoader.is_video_file(filename)

        if not is_audio_video:
            raise Exception("File is not an audio or video file")

        # Process audio/video file
        await task_queue.update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            progress="Transcribing audio...",
            progress_percent=40
        )

        # Prepare audio for transcription (extract from video if needed)
        audio_bytes, audio_ext = AudioVideoLoader.prepare_audio_for_transcription(
            content, filename
        )

        # Get audio duration
        duration = AudioVideoLoader.get_audio_duration(audio_bytes, audio_ext)

        # Transcribe audio using transcription manager
        transcription_manager = TranscriptionManager()
        # Transcribe audio with progress callback
        async def transcription_progress_callback(message: str, percent: int):
            await task_queue.update_task_status(
                task_id,
                TaskStatus.PROCESSING,
                progress=message,
                progress_percent=percent
            )

        transcription_result = await transcription_manager.transcribe_async(
            audio_bytes, language=language, file_extension=audio_ext, progress_callback=transcription_progress_callback
        )

        # Use transcribed text
        transcription_text = transcription_result["text"]
        detected_language = transcription_result["language"]

        await task_queue.update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            progress=f"Transcription complete ({len(transcription_text)} characters)",
            progress_percent=90
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Update task with results (using summary field for transcription text)
        await task_queue.update_task_result(
            task_id=task_id,
            summary=transcription_text,  # Full transcription text
            chunk_count=0,
            total_tokens=0,
            processing_time=processing_time,
            transcription_duration=duration,
            transcription_text_length=len(transcription_text)
        )

    except Exception as e:
        # Mark task as failed
        await task_queue.mark_task_failed(task_id, str(e))


@router.post("/transcribe/async")
async def transcribe_audio_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio/Video file to transcribe"),
    language: str = Form(None, description="Language code (e.g., 'zh' for Chinese, 'en' for English, None for auto-detect)")
):
    """
    Asynchronously transcribe audio/video file to text (no summarization).
    Returns a task_id for status polling.

    This endpoint only performs speech-to-text transcription without summarization.

    - **file**: Audio/Video file (MP3, WAV, M4A, MP4, AVI, MOV, MKV)
    - **language**: Optional language code to improve accuracy (zh, en, ja, etc.)

    Returns task_id for polling status via GET /task/{task_id}
    """
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        allowed_extensions = [
            '.mp3', '.wav', '.m4a',  # Audio
            '.mp4', '.avi', '.mov', '.mkv'  # Video
        ]

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Validate file size
        file_size = len(content)
        if file_size > settings.max_audio_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1_000_000:.2f} MB) exceeds maximum allowed size ({settings.max_audio_file_size / 1_000_000:.2f} MB)"
            )

        # Create task
        task_id = await task_queue.create_task(
            filename=file.filename,
            file_size=file_size
        )

        # Start background processing
        background_tasks.add_task(
            transcribe_audio_background,
            task_id=task_id,
            content=content,
            filename=file.filename,
            file_extension=file_extension,
            language=language
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": "Transcription started. Use the task_id to poll for status.",
            "poll_endpoint": f"/api/summarize/task/{task_id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start transcription: {str(e)}")


# Pydantic models for API requests
from pydantic import BaseModel

class SwitchProviderRequest(BaseModel):
    provider: str  # "local" or "cloud"


# Dependency to get transcription manager
def get_transcription_manager():
    return TranscriptionManager()


@router.get("/transcription-status")
async def get_transcription_status():
    """Get current transcription provider status."""
    try:
        manager = get_transcription_manager()
        provider_info = manager.get_provider_info()

        return {
            "success": True,
            "message": "Transcription status retrieved successfully",
            "provider_info": provider_info
        }
    except Exception as e:
        logger.error(f"Failed to get transcription status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get transcription status: {str(e)}")


@router.post("/switch-transcription-provider")
async def switch_transcription_provider(request: SwitchProviderRequest):
    """Switch transcription provider between local and cloud."""
    try:
        manager = get_transcription_manager()

        # Validate provider
        if request.provider not in ["local", "cloud"]:
            raise HTTPException(status_code=400, detail="Provider must be 'local' or 'cloud'")

        # Switch provider
        manager.switch_provider(request.provider)
        provider_info = manager.get_provider_info()

        return {
            "success": True,
            "message": f"Switched to {request.provider} transcription provider successfully",
            "provider_info": provider_info
        }
    except Exception as e:
        logger.error(f"Failed to switch transcription provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to switch transcription provider: {str(e)}")
