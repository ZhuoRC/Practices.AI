# AI Audio TTS Backend

FastAPI application for text-to-speech generation using multiple TTS providers.

## Port Configuration

- **Backend Port**: 7000
- **Frontend Port**: 3000 (proxy configured to backend at 7000)

## Setup and Running

### Method 1: Using Startup Scripts (Recommended)

#### Windows:
```bash
# Double-click or run from command line
start.bat
```

#### Linux/Mac:
```bash
# Make script executable (run once)
chmod +x start.sh

# Run the backend
./start.sh
```

### Method 2: Manual Setup

1. **Create Virtual Environment** (if not exists):
   ```bash
   # Windows
   python -m venv venv

   # Linux/Mac
   python3 -m venv venv
   ```

2. **Activate Virtual Environment**:
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Backend**:
   ```bash
   python main.py
   ```

## Environment Variables

Create a `.env` file in the backend directory with your API keys:

```env
# Backend Configuration
HOST=0.0.0.0
PORT=7000

# Azure TTS
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus

# Google Cloud TTS
GOOGLE_TTS_KEY=your_google_tts_key
GOOGLE_TTS_PROJECT_ID=your_project_id

# ElevenLabs TTS
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Local TTS (Optional)
LOCAL_TTS_MODEL_PATH=./models
LOCAL_TTS_DEFAULT_VOICE=en-us-lessac-medium

# Output Directory
OUTPUT_DIR=./generated_audio
```

## API Endpoints

- **Health Check**: `GET /health`
- **Providers**: `GET /providers`
- **Generate Speech**: `POST /generate`
- **Audio Download**: `GET /audio/{audio_id}`
- **API Documentation**: `http://localhost:7000/docs`

## Access URLs

- **Backend API**: http://localhost:7000
- **Interactive Docs**: http://localhost:7000/docs
- **OpenAPI Schema**: http://localhost:7000/openapi.json

## Logging

The application logs to both:
- Console output
- File: `app.log` (in the backend directory)

## Features

- Multiple TTS providers (Azure, Google, ElevenLabs, Local)
- Audio format conversion (MP3, WAV, OGG, FLAC)
- Voice preview functionality
- Health monitoring
- CORS support for frontend integration
- Request/response logging