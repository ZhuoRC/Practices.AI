from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import summarize
from .config import settings

# Create FastAPI app
app = FastAPI(
    title="Document Summarizer API",
    description="""
## Document Summarization System using Map-Reduce

This API provides intelligent document summarization using a Map-Reduce approach:

### Features
- **Document Upload**: Support for PDF, TXT, DOCX, MD files
- **Webpage Summarization**: Summarize web content from URLs
- **Map-Reduce Architecture**:
  - **Map Phase**: Each text chunk (800-1200 chars) is individually summarized
  - **Reduce Phase**: Chunk summaries are combined into a coherent final summary
- **Smart Chunking**: Respects sentence boundaries and language-specific punctuation
- **Dual LLM Support**: Works with both local Ollama and cloud APIs

### Workflow
1. **Load**: Extract text from documents (PDF, DOCX, TXT) or webpages
2. **Chunk**: Split text into 800-1200 character chunks at sentence boundaries
3. **Map**: Generate summary for each chunk independently
4. **Reduce**: Combine all chunk summaries into final comprehensive summary

### Getting Started
1. Upload a document at `/api/summarize/document`
2. Or summarize a webpage at `/api/summarize/webpage`
3. Check system health at `/api/summarize/health`
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "summarize",
            "description": "Document and webpage summarization operations using Map-Reduce",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarize.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Document Summarizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/summarize/health"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("=" * 60)
    print("Document Summarizer API Starting...")
    print("=" * 60)
    print(f"LLM Provider: {settings.llm_provider.upper()}")
    if settings.llm_provider.lower() == "local":
        print(f"  Local Ollama URL: {settings.ollama_base_url}")
        print(f"  Local Model: {settings.ollama_model}")
    elif settings.llm_provider.lower() == "cloud":
        print(f"  Cloud API URL: {settings.qwen_api_base_url}")
        print(f"  Cloud Model: {settings.qwen_model}")
    print(f"Chunking: {settings.min_chunk_size}-{settings.max_chunk_size} chars")
    print(f"Document Storage: {settings.document_storage_path}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("Document Summarizer API Shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
