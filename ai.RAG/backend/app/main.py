import os
# Disable ChromaDB telemetry before any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import documents, query
from .config import settings

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="RESTful API for RAG (Retrieval-Augmented Generation) system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("=" * 50)
    print("RAG System API Starting...")
    print("=" * 50)
    print(f"LLM Provider: {settings.llm_provider.upper()}")
    if settings.llm_provider.lower() == "local":
        print(f"  Local Ollama URL: {settings.ollama_base_url}")
        print(f"  Local Model: {settings.ollama_model}")
    elif settings.llm_provider.lower() == "cloud":
        print(f"  Cloud API URL: {settings.qwen_api_base_url}")
        print(f"  Cloud Model: {settings.qwen_model}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"ChromaDB: {settings.chroma_persist_directory}")
    print(f"PDF Storage: {settings.pdf_storage_path}")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("RAG System API Shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
