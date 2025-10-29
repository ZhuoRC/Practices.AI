# Quick Start Guide

## Step 1: Prepare Qwen API

Ensure your Qwen API service is accessible:

```bash
# For Aliyun DashScope (recommended)
# Get your API key from https://dashscope.console.aliyun.com/

# For local Qwen API (assuming it runs on localhost:8000)
curl http://localhost:8000/v1/models
```

If not started yet, refer to your Qwen API project documentation to start the service.

## Step 2: Install Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Backend

Check `backend/.env` file and ensure the configuration is correct:

```env
# LLM Provider: "cloud" or "local"
LLM_PROVIDER=cloud

# DashScope Configuration (if using cloud)
QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your-api-key-here
QWEN_MODEL=qwen3-32b

# Ollama Configuration (if using local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct

# Embedding Model
EMBEDDING_MODEL=BAAI/bge-m3

# RAG Configuration
TOP_K=8
PROMPT_TEMPLATE_FILE=rag_system.txt
```

**For local Ollama users**: See [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) for setup instructions.

## Step 4: Start Backend

```bash
cd backend
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

Visit API documentation: http://localhost:8001/docs

## Step 5: Install Frontend

```bash
cd frontend

# Install dependencies
npm install
```

## Step 6: Start Frontend

```bash
npm run dev
```

You should see:
```
Local: http://localhost:5173/
```

## Step 7: Use the System

1. **Open browser**: Visit http://localhost:5173
2. **Upload PDF**: Drag and drop or click to upload PDF files
3. **Wait for processing**: System will extract text and generate embeddings
4. **Ask questions**: Type your question in the chat interface
5. **View answers**: Get AI-generated answers with source citations

## Configuration Tips

### Choose Embedding Model

```env
# BGE-M3: Better for Chinese and multilingual (1024-dim)
EMBEDDING_MODEL=BAAI/bge-m3

# MiniLM: Lightweight and fast (384-dim)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Important**: Changing embedding model requires re-uploading all documents!

### Adjust Retrieval Settings

```env
# More chunks = more context but higher cost
TOP_K=10

# Fewer chunks = faster response
TOP_K=3
```

### Switch Prompt Templates

```env
# Simple and factual (default)
PROMPT_TEMPLATE_FILE=rag_system.txt

# Detailed with citations
PROMPT_TEMPLATE_FILE=rag_detailed.txt

# Chinese language
PROMPT_TEMPLATE_FILE=rag_chinese.txt
```

See `backend/app/prompts/README.md` for creating custom templates.

## Quick Test

Test the API with curl:

```bash
# Health check
curl http://localhost:8001/api/health

# List documents
curl http://localhost:8001/api/documents/

# Ask a question (after uploading documents)
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "include_sources": true}'
```

Or use the test script:

```bash
cd backend
python test_api.py path/to/your/test.pdf
```

## Troubleshooting

### Backend Issues

**Port already in use**:
```bash
# Change port in .env
PORT=8002
```

**Qwen API connection error**:
- Check API key is correct
- Verify API endpoint URL
- Ensure you have API credits

**ChromaDB telemetry warnings**:
- These are harmless and suppressed in the latest code
- Ignore if functionality works correctly

### Frontend Issues

**Cannot connect to backend**:
- Ensure backend is running on port 8001
- Check browser console for errors
- Verify no CORS issues

**Upload fails**:
- Check PDF file is valid
- Ensure file is not password-protected
- Check backend logs for errors

## Next Steps

- Read the full [README.md](README.md)
- Customize prompts in `backend/app/prompts/`
- Explore API at http://localhost:8001/docs
- Check PROJECT_SUMMARY.md for architecture details

Happy querying! 🚀
