# RAG Intelligent Q&A System

A local intelligent question-answering system based on Retrieval-Augmented Generation (RAG) technology, supporting PDF document upload, vector storage, and intelligent Q&A.

## Features

- 📄 **PDF Document Upload**: Support drag-and-drop PDF file upload
- 🔍 **Intelligent Retrieval**: Document retrieval based on vector similarity
- 💬 **Intelligent Q&A**: Generate answers combining retrieval results and large language models
- 📊 **Document Management**: View and manage uploaded documents
- 🎯 **Source Tracing**: Display reference document chunks and similarity scores

## Tech Stack

### Backend
- **Web Framework**: FastAPI
- **Large Language Model**: Qwen API (Local or Aliyun DashScope)
- **Vector Database**: ChromaDB
- **Text Embedding**: sentence-transformers (BGE-M3)
- **PDF Processing**: PyPDF2, LangChain

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Component Library**: Ant Design 5
- **HTTP Client**: Axios

## Project Structure

```
ai.RAG/
├── backend/              # Python backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   ├── prompts/     # Prompt templates
│   │   ├── config.py    # Configuration
│   │   └── main.py      # Main application
│   ├── requirements.txt # Python dependencies
│   ├── run.py          # Startup script
│   └── .env            # Environment variables
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API services
│   │   └── App.tsx     # Main component
│   └── package.json    # Node dependencies
└── data/               # Data storage
    ├── pdfs/          # PDF files
    └── chroma_db/     # Vector database
```

## Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Node.js 16+** and npm
3. **Qwen API** service (Local or Aliyun DashScope)

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**🚀 GPU Acceleration (Optional but Recommended)**

If you have an NVIDIA GPU, install GPU-accelerated PyTorch for **10-50x faster embedding generation**:

```bash
# After installing requirements.txt
pip install -r requirements-gpu.txt
```

See [GPU_SETUP.md](backend/GPU_SETUP.md) for detailed GPU setup instructions.

### 2. Configure Environment Variables

Edit `backend/.env` file:

```env
# Qwen API Configuration
QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your-api-key-here
QWEN_MODEL=qwen3-32b

# Embedding Model
EMBEDDING_MODEL=BAAI/bge-m3

# Server Configuration
HOST=0.0.0.0
PORT=8001

# Text Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# RAG Configuration
TOP_K=8
PROMPT_TEMPLATE_FILE=rag_system.txt
```

### 3. Start Backend Service

```bash
cd backend
python run.py
```

The backend service will start at `http://localhost:8001`.

Visit API documentation: `http://localhost:8001/docs`

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Start Frontend Development Server

```bash
npm run dev
```

The frontend will start at `http://localhost:5173`.

## Usage

1. **Upload Documents**: Drag and drop PDF files or click to select files
2. **Wait for Processing**: The system will extract text, chunk it, and generate embeddings
3. **Ask Questions**: Type your question in the chat interface
4. **View Answers**: The system retrieves relevant document chunks and generates answers
5. **Check Sources**: View the source chunks and similarity scores

## API Endpoints

### Document Management

- `POST /api/documents/upload` - Upload PDF document
- `GET /api/documents/` - List all documents
- `DELETE /api/documents/{document_id}` - Delete document

### Query

- `POST /api/query` - Ask a question
- `GET /api/health` - Health check

## Configuration

### LLM Provider

The system supports two LLM providers:
- **Cloud**: Aliyun DashScope cloud-based Qwen models
- **Local**: Run Qwen models locally on your machine via Ollama

See [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) for detailed setup instructions.

**Quick configuration:**
```bash
# Edit backend/.env
LLM_PROVIDER=cloud  # or "local"
```

### Other Settings

See `backend/.env.example` for all available configuration options:

- **LLM Provider**: Choose between cloud (DashScope) or local (Ollama)
- **Embedding Model**: Choose your embedding model (BGE-M3, MiniLM, etc.)
- **Vector Database**: ChromaDB persistence settings
- **Text Chunking**: Chunk size and overlap parameters
- **RAG Retrieval**: Number of chunks to retrieve (TOP_K)
- **Prompt Templates**: Select from multiple prompt templates

## Customizing Prompts

The system supports multiple prompt templates. See `backend/app/prompts/README.md` for details.

Available templates:
- `rag_system.txt` - Simple, factual prompt (default)
- `rag_detailed.txt` - Detailed prompt with citations
- `rag_chinese.txt` - Chinese language prompt

To create a custom template:
1. Create a new `.txt` file in `backend/app/prompts/`
2. Use `{context}` and `{question}` as placeholders
3. Update `PROMPT_TEMPLATE_FILE` in `.env`
4. Restart the server

## Development

### Backend Testing

```bash
cd backend
python test_api.py path/to/test.pdf
```

### Frontend Development

```bash
cd frontend
npm run dev
```

## License

This project is for educational and research purposes.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Ant Design](https://ant.design/)
- [Qwen](https://github.com/QwenLM/Qwen)
