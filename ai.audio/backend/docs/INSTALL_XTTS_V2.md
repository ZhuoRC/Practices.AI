# Installing Coqui XTTS-v2 Provider

XTTS-v2 is a high-quality multilingual TTS model with voice cloning capabilities. Here's how to set it up:

## Features

- **17 languages supported**: English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean, Hindi
- **Voice cloning**: Clone any voice with just a 6-second audio clip
- **Cross-lingual synthesis**: Use a voice sample in one language to generate speech in another
- **High quality**: 24kHz output with natural prosody
- **Emotion preservation**: Maintains emotional content from voice samples

## Installation Steps

### 1. Install Dependencies

```bash
cd ai.audio/backend
pip install TTS>=0.22.0 torch>=2.0.0 torchaudio>=2.0.0
```

### 2. Automatic Model Download

The XTTS-v2 model will be automatically downloaded the first time you use it (approximately 2-3 GB).

### 3. Optional: Voice Cloning Setup

Create a directory for voice samples:
```bash
mkdir voice_samples
```

Add 6+ second audio samples (WAV format) to the `voice_samples/` directory:
- Each sample should be clean speech without background noise
- Recommended sample rate: 22050Hz or higher
- File format: WAV
- Naming: `my_voice.wav` will be available as "Cloned: My Voice"

## Configuration

Add these to your `.env` file:

```env
# XTTS-v2 Configuration
XTTS_V2_DEFAULT_SPEAKER=default
XTTS_V2_DEFAULT_LANGUAGE=en
XTTS_V2_MODEL_PATH=              # Optional: Path to local model
XTTS_V2_USE_GPU=false            # Set to 'true' if you have CUDA GPU
XTTS_V2_VOICE_SAMPLES_PATH=./voice_samples
```

## Usage

### Basic Text-to-Speech

Select "xtts_v2" as provider in the frontend and choose:
- `default_female` - Default female voice
- `default_male` - Default male voice

### Voice Cloning

1. Add a 6+ second WAV file to `voice_samples/` (e.g., `my_voice.wav`)
2. Restart the backend
3. Select "xtts_v2" provider
4. Choose "Cloned: My Voice" from the voice list

### Multilingual Support

XTTS-v2 automatically detects language from voice_id:
- `default_female` (English)
- `default_female_zh` (Chinese)
- `default_female_es` (Spanish)
- etc.

## Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| en   | English | ja   | Japanese |
| es   | Spanish | hu   | Hungarian |
| fr   | French | ko   | Korean |
| de   | German | hi   | Hindi |
| it   | Italian | pt   | Portuguese |
| pl   | Polish | ru   | Russian |
| tr   | Turkish | nl   | Dutch |
| zh   | Chinese | cs   | Czech |
| ar   | Arabic |      |          |

## Performance Notes

- **CPU**: Takes 10-30 seconds per synthesis
- **GPU**: Much faster (1-5 seconds) if CUDA is available
- **Memory**: Requires ~4GB RAM for model loading
- **Storage**: Model files are ~2-3GB

## Troubleshooting

### Model Download Issues
- Check internet connection
- Ensure enough disk space (3GB+)
- Try restarting the backend

### GPU Not Working
- Verify CUDA installation: `nvidia-smi`
- Install PyTorch with CUDA support
- Set `XTTS_V2_USE_GPU=true` in `.env`

### Voice Cloning Not Working
- Ensure audio samples are 6+ seconds
- Check sample format (WAV required)
- Verify samples are in the correct directory
- Check backend logs for errors

## Quality Tips

**For Best Voice Cloning:**
- Use high-quality audio samples (16kHz+)
- Single speaker, no background noise
- 6-30 seconds of continuous speech
- Natural speaking style

**For Best Quality:**
- Use appropriate language codes
- Keep text under 500 characters for best results
- GPU acceleration recommended for speed
- Allow model to fully load before first use