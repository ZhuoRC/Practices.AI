from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ..services.rag import rag_service

router = APIRouter(prefix="/api", tags=["query"])


class QueryRequest(BaseModel):
    """Query request model"""
    question: str = Field(..., description="Question to ask the RAG system", min_length=1)
    top_k: Optional[int] = Field(None, description="Number of relevant chunks to retrieve (default: 3)", ge=1, le=10)
    include_sources: bool = Field(True, description="Whether to include source chunks in the response")
    document_ids: Optional[List[str]] = Field(None, description="Optional list of document IDs to filter search results (if empty, searches all documents)")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the main features of this product?",
                "top_k": 3,
                "include_sources": True,
                "document_ids": ["doc_20240101_120000_abc123"]
            }
        }


class SourceChunk(BaseModel):
    """Source chunk information"""
    chunk_index: int = Field(..., description="Index of the chunk in the search results")
    text: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata including document_id, original filename, etc.")
    similarity_score: float = Field(..., description="Similarity score (0-1)")


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    success: bool = Field(True, description="Whether the query was successful")
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="Generated answer based on the documents")
    retrieved_chunks: int = Field(..., description="Number of chunks retrieved")
    time_consumed: float = Field(..., description="Time consumed in seconds")
    total_tokens: int = Field(..., description="Total tokens used")
    prompt_tokens: int = Field(..., description="Prompt tokens used")
    completion_tokens: int = Field(..., description="Completion tokens used")
    sources: Optional[List[SourceChunk]] = Field(None, description="Source chunks used to generate the answer")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "question": "What are the main features?",
                "answer": "Based on the documents, the main features include...",
                "retrieved_chunks": 3,
                "time_consumed": 1.25,
                "total_tokens": 450,
                "prompt_tokens": 350,
                "completion_tokens": 100,
                "sources": [
                    {
                        "chunk_index": 0,
                        "text": "Sample chunk text...",
                        "metadata": {
                            "document_id": "doc_20240101_120000_abc123",
                            "original_filename": "sample.pdf"
                        },
                        "similarity_score": 0.85
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    success: bool = Field(..., description="Whether the health check passed")
    status: str = Field(..., description="System status (healthy/degraded/error)")
    vector_store: Optional[Dict[str, int]] = Field(None, description="Vector store statistics")
    llm_provider: Optional[str] = Field(None, description="LLM provider (cloud/local)")
    llm_model: Optional[str] = Field(None, description="LLM model name")
    llm_status: Optional[str] = Field(None, description="LLM service status")
    embedding_model: Optional[str] = Field(None, description="Embedding model name")
    error: Optional[str] = Field(None, description="Error message if status is error")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status": "healthy",
                "vector_store": {
                    "total_chunks": 150,
                    "total_documents": 5
                },
                "llm_provider": "cloud",
                "llm_model": "qwen3-32b",
                "llm_status": "healthy",
                "embedding_model": "BAAI/bge-m3"
            }
        }


@router.post("/query", response_model=QueryResponse, summary="Query RAG System")
async def query_rag(request: QueryRequest):
    """
    Ask a question to the RAG system and get an answer based on uploaded documents.

    The system will:
    1. Convert your question into an embedding
    2. Search for the most relevant document chunks
    3. Use those chunks as context for the LLM
    4. Generate a comprehensive answer

    **Note**: You must upload documents before querying the system.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources,
            document_ids=request.document_ids
        )

        return {
            "success": True,
            "question": request.question,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """
    Check the health status of the RAG system and its components.

    Returns the operational status of:
    - LLM service (Local Ollama or Cloud API)
    - Embedding service
    - Vector database
    - Document storage
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
