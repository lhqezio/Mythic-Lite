# Text-to-Speech (TTS) Setup Guide

## Overview

The Mythic-Lite TTS system uses **Piper TTS** to convert text to speech with high-quality, natural-sounding voices. The system automatically downloads voice models from the Hugging Face repository.

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# For audio playback, you may also need system packages:
# Ubuntu/Debian:
sudo apt install portaudio19-dev python3-pyaudio
# macOS:
brew install portaudio
# Windows:
# PyAudio should install automatically
```

### 2. Basic Usage

```python
from mythic_lite.workers.tts_worker import TTSWorker

# Create TTS worker
tts = TTSWorker()

# Initialize (downloads models automatically)
if tts.initialize():
    # Speak text
    tts.speak("Hello, this is a test!")
else:
    print(f"TTS failed to initialize: {tts.initialization_error}")
```

### 3. Available Voices

The system supports multiple Piper voices with different quality levels:

| Voice Name | Quality | Path |
|------------|---------|------|
| `amy-low` | Low (fast) | `en/en_US/amy/low` |
| `amy-medium` | Medium | `en/en_US/amy/medium` |
| `amy-high` | High (slow) | `en/en_US/amy/high` |
| `jenny-low` | Low (fast) | `en/en_US/jenny/low` |
| `jenny-medium` | Medium | `en/en_US/jenny/medium` |
| `jenny-high` | High (slow) | `en/en_US/jenny/high` |
| `karen-low` | Low (fast) | `en/en_US/karen/low` |
| `karen-medium` | Medium | `en/en_US/karen/medium` |
| `karen-high` | High (slow) | `en/en_US/karen/high` |
| `chris-low` | Low (fast) | `en/en_US/chris/low` |
| `chris-medium` | Medium | `en/en_US/chris/medium` |
| `chris-high` | High (slow) | `en/en_US/chris/high` |

### 4. Configuration

Set voice and audio settings via environment variables:

```bash
# Voice selection
export TTS_VOICE_PATH=amy-medium

# Audio settings
export TTS_SAMPLE_RATE=22050
export TTS_CHANNELS=1
export TTS_AUDIO_FORMAT=paInt16
export TTS_ENABLE_AUDIO=true
```

Or use a `.env` file:

```env
TTS_VOICE_PATH=amy-medium
TTS_SAMPLE_RATE=22050
TTS_CHANNELS=1
TTS_AUDIO_FORMAT=paInt16
TTS_ENABLE_AUDIO=true
```

## Troubleshooting

### Common Issues

#### 1. "huggingface_hub not available"

**Problem**: TTS models can't be downloaded.

**Solution**: Install the huggingface-hub package:
```bash
pip install huggingface-hub
```

#### 2. "PyAudio initialization failed"

**Problem**: Audio playback isn't working.

**Solution**: Install system audio packages:

**Ubuntu/Debian:**
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install PyAudio
```

**Windows:**
```bash
pip install PyAudio
```

#### 3. "No module named 'numpy'"

**Problem**: Missing numerical computing library.

**Solution**: Install numpy:
```bash
pip install numpy
```

#### 4. "Failed to download TTS model"

**Problem**: Models can't be downloaded from Hugging Face.

**Solutions**:
- Check internet connection
- Verify the model repository exists: https://huggingface.co/rhasspy/piper-voices
- Check if you have access to the repository
- Try a different voice (e.g., `amy-low` instead of `amy-high`)

### 5. Audio Quality Issues

**Problem**: Audio sounds distorted or choppy.

**Solutions**:
- Use a higher quality voice (e.g., `amy-medium` instead of `amy-low`)
- Increase sample rate: `TTS_SAMPLE_RATE=44100`
- Check system audio settings
- Ensure no other applications are using the audio device

## Advanced Usage

### Custom Voice Configuration

```python
from mythic_lite.core.config import TTSConfig

# Create custom TTS config
tts_config = TTSConfig(
    voice_path="amy-medium",
    sample_rate=44100,
    channels=2,  # Stereo
    audio_format="paFloat32",
    enable_audio=True
)

# Use custom config
tts = TTSWorker(config=tts_config)
```

### Audio Streaming

```python
# Generate audio without playing
audio_data = tts.text_to_speech_stream("Hello world")

# Save to file
with open("output.wav", "wb") as f:
    f.write(audio_data)

# Or play manually
tts.play_audio_stream(audio_data)
```

### Performance Monitoring

```python
# Get performance statistics
stats = tts.get_performance_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Audio generated: {stats['total_audio_generated']} bytes")
print(f"Average generation time: {stats['average_generation_time']:.2f}s")
```

## Voice Model Details

### Model Files

Each voice requires two files:
- **`.onnx`**: The neural network model for speech synthesis
- **`.onnx.json`**: Configuration file with voice parameters

### Model Locations

Models are automatically downloaded to:
```
~/.cache/huggingface/hub/models--rhasspy--piper-voices/
```

### Model Sizes

| Quality | Approximate Size | Download Time |
|---------|------------------|---------------|
| Low | ~10-15 MB | 1-2 minutes |
| Medium | ~20-30 MB | 2-4 minutes |
| High | ~40-60 MB | 4-8 minutes |

## Examples

See `examples/tts_example.py` for a complete working example.

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify all dependencies are installed
3. Check the logs for detailed error messages
4. Try with a different voice quality
5. Ensure your system supports the audio format

## Performance Tips

- Use `low` quality voices for faster generation
- Use `high` quality voices for better audio quality
- Close other audio applications during TTS use
- Consider using a dedicated audio device for production use