from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.rag import rag_service

router = APIRouter(prefix="/api", tags=["query"])


class QueryRequest(BaseModel):
    """Query request model"""
    question: str
    top_k: Optional[int] = None
    include_sources: bool = True


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str


@router.post("/query")
async def query_rag(request: QueryRequest):
    """
    Execute RAG query

    Args:
        request: Query request with question and options

    Returns:
        Answer with optional source chunks
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources
        )

        return {
            "success": True,
            "question": request.question,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Check system health

    Returns:
        System health status
    """
    try:
        health = await rag_service.health_check()

        return {
            "success": True,
            **health
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }
