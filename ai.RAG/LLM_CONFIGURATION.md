# LLM Configuration Guide

The RAG system supports two LLM providers: **Cloud** (DashScope) and **Local** (Ollama).

## Quick Start

Edit `backend/.env` and set the `LLM_PROVIDER` variable:

```bash
# For cloud Qwen (DashScope)
LLM_PROVIDER=cloud

# For local Qwen (Ollama)
LLM_PROVIDER=local
```

## Option 1: DashScope (Cloud) - Recommended for Production

### Advantages
- ✅ No local GPU required
- ✅ Powerful models (qwen3-32b, qwen-plus, qwen-max)
- ✅ Fast and reliable
- ✅ Automatic scaling

### Setup

1. **Get API Key**
   - Visit: https://dashscope.console.aliyun.com/
   - Create account and get your API key

2. **Configure `.env`**
   ```bash
   LLM_PROVIDER=cloud
   QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY=sk-your-api-key-here
   QWEN_MODEL=qwen3-32b
   ```

3. **Available Models**
   - `qwen3-32b` - Latest model, best performance
   - `qwen-plus` - Balanced performance and cost
   - `qwen-turbo` - Fast and economical
   - `qwen-max` - Most powerful

4. **Cost**
   - Pay-per-use pricing
   - Check current rates at: https://dashscope.console.aliyun.com/

## Option 2: Ollama (Local) - Best for Privacy

### Advantages
- ✅ Complete privacy (no data sent to cloud)
- ✅ No API costs
- ✅ Works offline
- ✅ Full control

### Requirements
- GPU with at least 8GB VRAM (for qwen2.5:7b)
- Or CPU with sufficient RAM (slower)

### Setup

1. **Install Ollama**

   **Windows:**
   - Download from: https://ollama.ai/download
   - Run the installer

   **Linux/Mac:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull Qwen Model**
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```

   This will download the model (~4.7GB).

3. **Verify Ollama is Running**
   ```bash
   ollama list
   ```

   Should show `qwen2.5:7b-instruct` in the list.

4. **Configure `.env`**
   ```bash
   LLM_PROVIDER=local
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:7b-instruct
   ```

5. **Available Models**
   - `qwen2.5:7b-instruct` - Recommended (4.7GB)
   - `qwen2.5:14b-instruct` - Better quality (9GB)
   - `qwen2.5:32b-instruct` - Best quality (20GB, requires 24GB+ VRAM)

   See all models: https://ollama.ai/library/qwen2.5

## Switching Between Providers

Just change `LLM_PROVIDER` in `.env` and restart:

```bash
# Switch to local Ollama
LLM_PROVIDER=local

# Switch to cloud DashScope
LLM_PROVIDER=cloud
```

Restart the backend:
```bash
cd backend
python run.py
```

## Verification

Check the startup logs:

**For Local (Ollama):**
```
==================================================
RAG System API Starting...
==================================================
LLM Provider: LOCAL
  Local Ollama URL: http://localhost:11434
  Local Model: qwen2.5:7b-instruct
...
```

**For Cloud (DashScope):**
```
==================================================
RAG System API Starting...
==================================================
LLM Provider: CLOUD
  Cloud API URL: https://dashscope.aliyuncs.com/compatible-mode/v1
  Cloud Model: qwen3-32b
...
```

## Testing

1. **Check Health Endpoint**
   ```bash
   curl http://localhost:8001/api/health
   ```

   Should show:
   ```json
   {
     "status": "healthy",
     "llm_provider": "local",  // or "cloud"
     "llm_model": "qwen2.5:7b-instruct",
     "llm_status": "healthy",
     ...
   }
   ```

2. **Test Query**

   Upload a document and ask a question to verify the LLM is working correctly.

## Troubleshooting

### DashScope Issues

**"Cannot connect to DashScope"**
- Check your API key is correct
- Verify you have API credits
- Check internet connection

**"HTTP error 401"**
- API key is invalid or expired
- Get a new key from: https://dashscope.console.aliyun.com/

### Ollama Issues

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama list`
- Check URL is correct: `http://localhost:11434`
- Try restarting Ollama

**"Model not found"**
- Pull the model: `ollama pull qwen2.5:7b-instruct`
- Verify model name in `.env` matches exactly

**Slow responses**
- Ollama is using CPU instead of GPU
- Check GPU is available: `ollama run qwen2.5:7b-instruct "test"`
- Consider using a smaller model

**Out of memory**
- Model is too large for your GPU
- Try smaller model: `qwen2.5:7b-instruct` (4.7GB)
- Or increase system RAM and use CPU mode

## Recommendations

### Development
- Use **Ollama** for local development
- No API costs, faster iteration
- Good for testing and debugging

### Production
- Use **DashScope** for production
- More reliable and powerful
- Better for handling concurrent users
- No hardware maintenance

### Privacy-Sensitive Applications
- Use **Ollama** exclusively
- All data stays on your infrastructure
- Full control over model and data

## Performance Comparison

| Aspect | DashScope | Ollama (7B) | Ollama (32B) |
|--------|-----------|-------------|--------------|
| Speed | Fast | Medium | Slow |
| Quality | Excellent | Good | Excellent |
| Cost | Pay-per-use | Free | Free |
| Privacy | Cloud | Local | Local |
| Setup | Easy | Medium | Hard |
| Hardware | None | 8GB+ VRAM | 24GB+ VRAM |

## Next Steps

- Configure your preferred provider in `.env`
- Restart the backend service
- Test with the health endpoint
- Upload documents and start querying!
