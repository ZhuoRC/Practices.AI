# AI Audio TTS Service

A comprehensive text-to-speech web application supporting multiple TTS providers including Azure Cognitive Services, Google Cloud TTS, ElevenLabs, and local TTS engines.

## Features

### 🎯 Core Functionality
- **Multi-Provider Support**: Azure, Google, ElevenLabs, and Local TTS
- **Voice Selection**: Browse and select from available voices per provider
- **Real-time Preview**: Test voices before generating full audio
- **Audio Controls**: Play, pause, seek, volume control
- **Multiple Formats**: MP3, WAV, OGG, FLAC support
- **Advanced Settings**: Speed, pitch, volume controls

### 🎨 User Interface
- **Modern Design**: Built with React and Ant Design
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Feedback**: Loading states and progress indicators
- **Provider Status**: Visual indicators for service availability
- **Voice Information**: Detailed voice metadata and descriptions

### 🔧 Technical Features
- **RESTful API**: Clean FastAPI backend
- **Async Processing**: Non-blocking audio generation
- **File Management**: Automatic cleanup and organization
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed request and response logging

## Quick Start

### Prerequisites

#### Backend
- Python 3.8+
- pip (Python package manager)

#### Frontend
- Node.js 16+
- npm (Node.js package manager)

#### Optional TTS Services
- Azure Cognitive Services account
- Google Cloud TTS API key
- ElevenLabs API key
- Piper TTS (for local processing)

### Installation

1. **Clone or download the project** to your desired location
2. **Navigate to the project directory**: `cd Practices.AI\ai.audio`

### Configuration

#### Backend Configuration
1. Copy `backend\.env` file and update with your API keys:
   ```env
   # Azure Cognitive Services
   AZURE_SPEECH_KEY=your_azure_key_here
   AZURE_SPEECH_REGION=eastus

   # Google Cloud TTS
   GOOGLE_TTS_KEY=your_google_key_here
   GOOGLE_TTS_PROJECT_ID=your_project_id

   # ElevenLabs
   ELEVENLABS_API_KEY=your_elevenlabs_key_here

   # Local TTS
   LOCAL_TTS_MODEL_PATH=./models
   LOCAL_TTS_DEFAULT_VOICE=en-us-lessac-medium
   ```

#### Frontend Configuration
- The frontend will automatically create a `.env` file with:
   ```env
   REACT_APP_API_URL=http://localhost:7000
   ```

### Running the Application

#### Option 1: Start Both Services (Recommended)
```bash
# Run the combined startup script
start.bat
```
This will start both backend (port 7000) and frontend (port 3000) in separate windows.

#### Option 2: Start Services Separately

**Backend only:**
```bash
start_backend.bat
```

**Frontend only:**
```bash
start_frontend.bat
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:7000
- **API Documentation**: http://localhost:7000/docs

## Usage Guide

### 1. Select a TTS Provider
- Choose from available providers in the left sidebar
- Provider status indicators show configuration state
- Each provider shows available capabilities

### 2. Configure Voice Settings
- **Text Input**: Enter your text (up to 5000 characters)
- **Voice Selection**: Browse available voices with preview
- **Audio Format**: Choose MP3, WAV, OGG, or FLAC
- **Advanced Controls**: Adjust speed, pitch, and volume

### 3. Generate Audio
- Click "生成语音" to start synthesis
- Monitor progress in real-time
- Audio automatically loads in the player when ready

### 4. Playback and Download
- Use the built-in audio player for playback
- Download generated audio files
- Share audio via download links

## API Reference

### Core Endpoints

#### Health Check
```http
GET /health
```

#### Get Providers
```http
GET /providers
```

#### Get Provider Voices
```http
GET /providers/{provider}/voices
```

#### Generate Speech
```http
POST /generate
Content-Type: application/json

{
  "text": "Hello, world!",
  "provider": "azure",
  "voice_id": "en-US-AriaNeural",
  "speed": 1.0,
  "pitch": 0.0,
  "volume": 1.0,
  "output_format": "mp3"
}
```

#### Get Audio
```http
GET /audio/{audio_id}
```

#### Voice Preview
```http
GET /voices/{provider}/{voice_id}/preview
```

### Response Examples

#### TTS Generation Response
```json
{
  "audio_id": "uuid-string",
  "duration": 2.45,
  "file_size": 15360,
  "format": "mp3",
  "provider_used": "azure",
  "voice_used": "en-US-AriaNeural",
  "sample_rate": 24000,
  "metadata": {
    "provider": "azure",
    "model": "neural"
  },
  "download_url": "/audio/uuid-string"
}
```

## Provider Setup

### Azure Cognitive Services
1. Create an Azure account
2. Create a Speech Service resource
3. Get your API key and region
4. Add to `.env` file:
   ```env
   AZURE_SPEECH_KEY=your_key
   AZURE_SPEECH_REGION=your_region
   ```

### Google Cloud TTS
1. Create a Google Cloud project
2. Enable Cloud Text-to-Speech API
3. Create service account key
4. Add to `.env` file:
   ```env
   GOOGLE_TTS_KEY=your_key
   GOOGLE_TTS_PROJECT_ID=your_project_id
   ```

### ElevenLabs
1. Create an ElevenLabs account
2. Get your API key from dashboard
3. Add to `.env` file:
   ```env
   ELEVENLABS_API_KEY=your_key
   ```

### Local TTS (Piper)
1. Install Piper TTS:
   ```bash
   # Download Piper binary
   # Add to PATH or place in project directory
   ```
2. Download voice models:
   ```bash
   # Example models included in /models directory
   # Additional models from Piper releases
   ```
3. Configure in `.env`:
   ```env
   LOCAL_TTS_MODEL_PATH=./models
   LOCAL_TTS_DEFAULT_VOICE=en-us-lessac-medium
   ```

## Troubleshooting

### Common Issues

#### Backend Won't Start
- **Check Python version**: Requires Python 3.8+
- **Install dependencies**: Run `pip install -r requirements.txt`
- **Check .env file**: Ensure all required variables are set

#### Frontend Won't Start
- **Check Node.js version**: Requires Node.js 16+
- **Install dependencies**: Run `npm install`
- **Check API URL**: Verify `REACT_APP_API_URL` in frontend .env

#### TTS Provider Errors
- **API Keys**: Verify keys are correct and active
- **Quotas**: Check provider usage limits
- **Network**: Ensure internet connection for cloud providers

#### Audio Generation Issues
- **Text length**: Most providers limit to 5000 characters
- **Unsupported characters**: Some providers have character restrictions
- **Voice availability**: Check if selected voice exists for provider

### Logging

#### Backend Logs
- Check `backend/app.log` for detailed error information
- Console output shows real-time request/response data

#### Frontend Logs
- Browser console shows API errors and warnings
- Network tab shows HTTP request details

## Development

### Project Structure
```
ai.audio/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── .env                # Environment variables
│   ├── requirements.txt      # Python dependencies
│   └── tts_services/       # TTS provider modules
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main application
│   ├── package.json        # Node dependencies
│   └── public/           # Static assets
├── start_backend.bat      # Backend startup script
├── start_frontend.bat     # Frontend startup script
├── start.bat             # Combined startup script
└── README.md             # This file
```

### Adding New TTS Providers

1. **Create Service Class**:
   ```python
   # backend/tts_services/new_provider.py
   class NewProviderTTSService(TTSService):
       async def get_available_voices(self) -> List[VoiceInfo]:
           # Return available voices
       
       async def synthesize(self, request: TTSRequest) -> TTSResponse:
           # Generate audio
   ```

2. **Register Service**:
   ```python
   # backend/main.py - TTSManager._initialize_services()
   self.services["new_provider"] = NewProviderTTSService(config)
   ```

3. **Add Frontend Support**:
   ```typescript
   # frontend/src/App.tsx - getProviderIcon, getProviderName
   const icons = { 'new_provider': <YourIcon /> }
   const names = { 'new_provider': 'Your Provider Name' }
   ```

### Customization

#### Adding New Audio Formats
1. **Backend**: Update `AudioFormat` enum in `base.py`
2. **Frontend**: Add format options to `App.tsx`
3. **Conversion**: Handle format conversion in TTS services

#### UI Customization
- **Colors**: Modify CSS variables in `App.css`
- **Layout**: Adjust Ant Design components in `App.tsx`
- **Components**: Extend React components in `components/`

## License

This project is for educational and demonstration purposes. Please respect the terms of service of all TTS providers used.

## Support

For issues and questions:
1. Check this README for troubleshooting
2. Review backend logs (`backend/app.log`)
3. Check browser console for frontend errors
4. Verify API key configuration in `.env` files

---

**Happy text-to-speech! 🎵**
