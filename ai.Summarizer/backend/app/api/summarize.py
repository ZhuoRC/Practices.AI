"""API endpoints for document summarization"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, HttpUrl
from typing import Optional
from pathlib import Path
import shutil
from ..services.summarizer import get_summarizer
from ..services.storage import get_storage
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
        allowed_extensions = ['.pdf', '.txt', '.docx', '.doc', '.md', '.text']

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
