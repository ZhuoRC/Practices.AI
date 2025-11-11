# XTTS-v2 Quick Start Guide

## 🚀 Fast Installation (5 minutes setup, 15-30 minutes first use)

### Step 1: Install Dependencies
```bash
# Navigate to backend directory
cd ai.audio/backend

# Run the automated installation script
install_xtts_v2.bat
```

### Step 2: Test Installation
```bash
# Run the test script to verify everything works
python test_xtts_v2.py
```

### Step 3: Start the Service
```bash
# Start the backend server
python start_backend.py
```

### Step 4: Use XTTS-v2
- Open frontend and select "xtts_v2" provider
- Or use API directly: `http://localhost:8000/api/tts/synthesize`

## 📋 What You Get

✅ **17 Languages** - English, Spanish, French, German, Chinese, Japanese, Korean, and more  
✅ **Voice Cloning** - Clone any voice from 6-second audio sample  
✅ **Cross-lingual** - Clone English voice to speak Chinese  
✅ **High Quality** - Natural, emotional speech  
✅ **Offline** - Works without internet after installation  
✅ **GPU Support** - Optional acceleration for faster processing  

## 🎯 Voice Cloning Setup

1. **Create voice samples directory** (already done by installer)
2. **Add audio files**: Place 6+ second WAV files in `voice_samples/`
   ```bash
   # Example: Add your voice sample
   copy my_voice.wav voice_samples\
   ```
3. **Restart the server**: Voice samples will be automatically detected
4. **Select cloned voice**: Choose "cloned_my_voice" from the voice list

## 🔧 Optional GPU Setup

If you have NVIDIA GPU:
```bash
# Install CUDA version of PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Enable GPU in environment
set XTTS_V2_USE_GPU=true

# Restart the server
python start_backend.py
```

## 📝 Quick Test Commands

```bash
# Test basic functionality
python -c "
from TTS.api import TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
tts.tts_to_file('Hello world!', language='en', file_path='test.wav')
print('Generated test.wav')
"

# Test multilingual
python -c "
from TTS.api import TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
tts.tts_to_file('Bonjour le monde!', language='fr', file_path='french.wav')
print('Generated french.wav')
"

# Test voice cloning (if you have voice_samples/my_voice.wav)
python -c "
from TTS.api import TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
tts.tts_to_file('This is my cloned voice!', speaker_wav='voice_samples/my_voice.wav', language='en', file_path='cloned.wav')
print('Generated cloned.wav')
"
```

## 🌐 API Usage Examples

### Basic Synthesis
```bash
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from XTTS-v2!",
    "voice_id": "default_female",
    "provider": "xtts_v2"
  }'
```

### Multilingual
```bash
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola mundo desde XTTS-v2!",
    "voice_id": "default_female",
    "provider": "xtts_v2"
  }'
```

### Voice Cloning
```bash
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is my cloned voice!",
    "voice_id": "cloned_my_voice",
    "provider": "xtts_v2"
  }'
```

## 🔍 Check Available Voices
```bash
curl http://localhost:8000/api/tts/voices?provider=xtts_v2
```

## 📊 Performance

| Setup | Synthesis Speed | Quality | Setup Time |
|-------|----------------|---------|------------|
| CPU | ~5-10 sec/100 chars | Excellent | 5 min |
| GPU | ~1-3 sec/100 chars | Excellent | 10 min |
| Voice Cloning | +2-5 sec | Excellent | - |

## 🆘 Troubleshooting

**Problem**: "TTS library not found"
```bash
# Solution: Install dependencies
pip install TTS>=0.22.0 torch torchaudio
```

**Problem**: "Model download failed"
```bash
# Solution: Check internet and disk space
# Model size: ~2.5GB
# Location: %USERPROFILE%\.local\share\tts\
```

**Problem**: "Voice cloning not working"
```bash
# Solution: Add voice samples
mkdir voice_samples
# Place 6+ second WAV files in voice_samples/
```

**Problem**: "GPU not detected"
```bash
# Solution: Install CUDA PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
set XTTS_V2_USE_GPU=true
```

## 📁 File Locations

- **Installation Script**: `install_xtts_v2.bat`
- **Test Script**: `test_xtts_v2.py`
- **Voice Samples**: `voice_samples/`
- **Model Storage**: `%USERPROFILE%\.local\share\tts\`
- **Documentation**: `XTTS_V2_INSTALLATION.md`

## 🎉 Ready to Use!

Once installation is complete, you have:
- ✅ Working XTTS-v2 TTS service
- ✅ Support for 17 languages
- ✅ Voice cloning capabilities
- ✅ REST API integration
- ✅ Frontend compatibility

Start creating amazing speech synthesis! 🎤→🔊
