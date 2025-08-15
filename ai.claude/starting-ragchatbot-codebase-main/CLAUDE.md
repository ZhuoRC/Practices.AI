# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

**Start the application:**
```bash
./run.sh
```

**Install dependencies:**
```bash
uv sync
```

**Manual server start:**
```bash
cd backend && uv run uvicorn app:app --reload --port 8000
```

## Architecture Overview

This is a full-stack RAG (Retrieval-Augmented Generation) system for querying course materials:

### Backend Architecture (Python/FastAPI)
- **FastAPI app** (`backend/app.py`) - Main web server with REST API endpoints
- **RAG System** (`backend/rag_system.py`) - Core orchestrator connecting all components
- **Vector Store** (`backend/vector_store.py`) - ChromaDB-based semantic search using sentence-transformers
- **AI Generator** (`backend/ai_generator.py`) - Anthropic Claude integration with tool-based responses
- **Document Processor** (`backend/document_processor.py`) - Processes course documents into chunks
- **Session Manager** (`backend/session_manager.py`) - Handles conversation history
- **Search Tools** (`backend/search_tools.py`) - Tool-based search system for Claude

### Frontend (Static HTML/JS)
- Simple web interface in `frontend/` directory
- Served statically by FastAPI at root path

### Data Models
- **Course**: Contains title, instructor, lessons
- **CourseChunk**: Text chunks with metadata for vector search
- **Lesson**: Individual lessons within courses

### Key Components Flow
1. Documents in `docs/` are processed into chunks on startup
2. Chunks are embedded and stored in ChromaDB 
3. User queries trigger semantic search via Claude tools
4. Claude generates responses using retrieved context
5. Session management maintains conversation history

## Environment Setup

Required environment variable in `.env`:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Development Notes

- Uses `uv` for Python package management
- ChromaDB data stored in `./chroma_db` (auto-created)
- Course documents loaded from `docs/` folder on startup
- No test framework currently configured
- No linting/formatting tools configured