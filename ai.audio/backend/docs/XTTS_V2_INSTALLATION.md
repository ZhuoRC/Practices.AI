# Coqui XTTS-v2 Installation Guide

## Overview

Coqui XTTS-v2 is a high-quality multilingual text-to-speech model with voice cloning capabilities. It supports 17 languages and can clone voices from just a 6-second audio sample.

## Features

- **17 Languages Supported**: English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean, Hindi
- **Voice Cloning**: Clone voices from 6+ second audio samples
- **Cross-lingual Voice Cloning**: Clone a voice in one language and use it in another
- **High Quality**: Natural-sounding speech with emotional expression
- **Offline Use**: Works completely offline after installation
- **GPU Acceleration**: Optional GPU support for faster inference

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 8GB RAM
- 5GB free disk space
- Internet connection for initial model download

### Recommended Requirements
- Python 3.9+
- 16GB+ RAM
- NVIDIA GPU with CUDA support (or AMD with ROCm)
- 10GB+ free disk space
- SSD for faster model loading

## Installation Methods

### Method 1: Automated Installation (Windows)

1. Navigate to the backend directory:
   ```bash
   cd ai.audio/backend
   ```

2. Run the installation script:
   ```bash
   install_xtts_v2.bat
   ```

This script will:
- Install all required Python packages
- Create necessary directories
- Test the installation
- Download the XTTS-v2 model on first use

### Method 2: Manual Installation

1. Install Python dependencies:
   ```bash
   pip install TTS>=0.22.0
   pip install torch>=2.0.0 torchaudio>=2.0.0
   pip install librosa soundfile numpy
   ```

2. Create voice samples directory:
   ```bash
   mkdir voice_samples
   ```

3. Test installation:
   ```python
   from TTS.api import TTS
   tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)
   ```

### Method 3: GPU Installation (Optional)

If you have an NVIDIA GPU with CUDA:

1. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. Set GPU usage environment variable:
   ```bash
   set XTTS_V2_USE_GPU=true
   ```

3. Install TTS library:
   ```bash
   pip install TTS>=0.22.0
   ```

## Configuration

### Environment Variables

Configure these variables in your `.env` file or system environment:

```bash
# XTTS-v2 Configuration
XTTS_V2_DEFAULT_SPEAKER=default
XTTS_V2_DEFAULT_LANGUAGE=en
XTTS_V2_USE_GPU=false
XTTS_V2_MODEL_PATH=
XTTS_V2_VOICE_SAMPLES_PATH=./voice_samples
```

### Voice Cloning Setup

1. **Create voice samples directory**:
   ```bash
   mkdir voice_samples
   ```

2. **Add voice samples**:
   - Place 6+ second WAV files in the `voice_samples/` directory
   - Recommended format: 22kHz+ mono WAV
   - Clean audio with minimal background noise works best
   - Example filename: `my_voice.wav`

3. **Voice sample recommendations**:
   - Duration: 6-30 seconds
   - Format: WAV, MP3, or FLAC
   - Sample rate: 22050Hz or higher
   - Channels: Mono (recommended)
   - Content: Natural speech with various emotions

## Usage

### Basic Text-to-Speech

```python
from TTS.api import TTS

# Initialize TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')

# Generate speech
tts.tts_to_file(
    text="Hello, this is XTTS-v2 speaking!",
    speaker=tts.speakers[0],
    language="en",
    file_path="output.wav"
)
```

### Voice Cloning

```python
from TTS.api import TTS

# Initialize TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')

# Clone voice from audio sample
tts.tts_to_file(
    text="This is my cloned voice speaking!",
    speaker_wav="voice_samples/my_voice.wav",
    language="en",
    file_path="cloned_output.wav"
)
```

### Cross-lingual Voice Cloning

```python
# Clone English voice to speak Chinese
tts.tts_to_file(
    text="你好，这是我的克隆声音在说中文！",
    speaker_wav="voice_samples/english_voice.wav",
    language="zh",
    file_path="cross_lingual_output.wav"
)
```

## API Integration

The XTTS-v2 service is already integrated into your audio backend. To use it:

1. **Start the backend server**:
   ```bash
   python start_backend.py
   ```

2. **Use via REST API**:
   ```bash
   # Get available voices
   curl http://localhost:8000/api/tts/voices?provider=xtts_v2

   # Generate speech
   curl -X POST http://localhost:8000/api/tts/synthesize \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello from XTTS-v2!",
       "voice_id": "default_female",
       "provider": "xtts_v2"
     }'
   ```

3. **Voice cloning via API**:
   ```bash
   curl -X POST http://localhost:8000/api/tts/synthesize \
     -H "Content-Type: application/json" \
     -d '{
       "text": "This is my cloned voice!",
       "voice_id": "cloned_my_voice",
       "provider": "xtts_v2"
     }'
   ```

## Supported Languages

| Language | Code | Voice Cloning | Cross-lingual |
|----------|------|---------------|---------------|
| English | en | ✓ | ✓ |
| Spanish | es | ✓ | ✓ |
| French | fr | ✓ | ✓ |
| German | de | ✓ | ✓ |
| Italian | it | ✓ | ✓ |
| Portuguese | pt | ✓ | ✓ |
| Polish | pl | ✓ | ✓ |
| Turkish | tr | ✓ | ✓ |
| Russian | ru | ✓ | ✓ |
| Dutch | nl | ✓ | ✓ |
| Czech | cs | ✓ | ✓ |
| Arabic | ar | ✓ | ✓ |
| Chinese | zh | ✓ | ✓ |
| Japanese | ja | ✓ | ✓ |
| Hungarian | hu | ✓ | ✓ |
| Korean | ko | ✓ | ✓ |
| Hindi | hi | ✓ | ✓ |

## Troubleshooting

### Common Issues

1. **Model download fails**:
   - Check internet connection
   - Ensure sufficient disk space (~2.5GB)
   - Try manual download from Hugging Face

2. **GPU not detected**:
   - Verify CUDA installation: `nvidia-smi`
   - Install PyTorch with CUDA support
   - Set `XTTS_V2_USE_GPU=true`

3. **Memory errors**:
   - Reduce batch size
   - Use CPU instead of GPU if limited VRAM
   - Close other applications using memory

4. **Voice cloning quality poor**:
   - Use longer audio samples (10-30 seconds)
   - Ensure clean, noise-free audio
   - Use consistent speaking style in samples

### Model Storage

Models are downloaded to:
- **Windows**: `%USERPROFILE%\.local\share\tts\`
- **Linux/Mac**: `~/.local/share/tts/`

### Performance Optimization

1. **GPU Acceleration**:
   ```bash
   # Install CUDA version of PyTorch
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # Enable GPU in environment
   export XTTS_V2_USE_GPU=true
   ```

2. **Model Caching**:
   - Keep models in local storage
   - Avoid frequent re-downloads
   - Use SSD for faster loading

3. **Memory Management**:
   - Limit concurrent requests
   - Use appropriate batch sizes
   - Monitor GPU memory usage

## Advanced Usage

### Custom Model Fine-tuning

For advanced users, XTTS-v2 can be fine-tuned on custom datasets:

```python
# Fine-tuning example (simplified)
from TTS.config import load_config
from TTS.tts.datasets import load_tts_samples

# Load configuration
config = load_config("xtts_v2_config.json")

# Load custom dataset
train_samples, eval_samples = load_tts_samples(
    dataset_config,
    eval_split=True,
    eval_split_max_size=config.eval_split_max_size,
    eval_split_size=config.eval_split_size
)

# Fine-tune model
# (This requires significant compute resources and custom setup)
```

### Batch Processing

```python
# Process multiple texts efficiently
texts = ["Hello world", "How are you?", "Goodbye"]
for i, text in enumerate(texts):
    tts.tts_to_file(
        text=text,
        speaker=tts.speakers[0],
        language="en",
        file_path=f"output_{i}.wav"
    )
```

## Support

- **Documentation**: https://coqui.ai/docs/
- **GitHub**: https://github.com/coqui-ai/TTS
- **Model Hub**: https://huggingface.co/coqui/XTTS-v2
- **Community**: https://discord.gg/coqui

## License

XTTS-v2 is released under the CPAL (Common Public Attribution License). Commercial use requires attribution to Coqui.
