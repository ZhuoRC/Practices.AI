# RAG System Backend

Backend service for the RAG system built with FastAPI.

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and modify the configuration:

```bash
cp .env.example .env
```

Edit `.env` to set your API keys and preferences.

### Run

```bash
python run.py
```

The service will start at http://localhost:8001

## API Documentation

After starting the service, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Directory Structure

```
backend/
├── app/
│   ├── api/                  # API routes
│   │   ├── documents.py      # Document management API
│   │   └── query.py          # Query API
│   ├── services/             # Business logic
│   │   ├── pdf_processor.py  # PDF processing
│   │   ├── embeddings.py     # Text embeddings
│   │   ├── vector_store.py   # Vector database
│   │   └── rag.py            # RAG core logic
│   ├── prompts/              # Prompt templates
│   │   ├── rag_system.txt    # Default prompt template
│   │   ├── rag_detailed.txt  # Detailed prompt template
│   │   ├── rag_chinese.txt   # Chinese prompt template
│   │   └── README.md         # Prompt templates guide
│   ├── config.py             # Configuration management
│   └── main.py               # FastAPI application
├── requirements.txt          # Python dependencies
└── run.py                    # Startup script
```

## Key Dependencies

- **FastAPI**: Web framework
- **ChromaDB**: Vector database
- **sentence-transformers**: Text embeddings (BGE-M3)
- **PyPDF2**: PDF processing
- **LangChain**: Text chunking
- **httpx**: HTTP client for Qwen API

## Features

### Document Management
- Upload PDF documents
- Automatic text extraction and chunking
- Vector embedding generation
- Document listing and deletion

### RAG Query
- Semantic search in vector database
- Context retrieval from documents
- LLM-powered answer generation
- Source citation support

### Customizable Prompts
- Multiple prompt templates
- Easy template switching via config
- Support for custom prompts
- See `app/prompts/README.md` for details

## Configuration Options

See `.env.example` for all available configuration options:
- Qwen API settings
- Embedding model selection
- Vector database configuration
- Text chunking parameters
- RAG retrieval settings
- Prompt template selection
