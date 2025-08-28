# Installation Guide

This guide covers all installation methods for Mythic-Lite, from quick automated setup to advanced manual configuration.

## 🚀 Quick Installation

### Windows (Recommended)

#### Option 1: Automated Batch File
1. Download the project and navigate to the `scripts` folder
2. Double-click `start_mythic.bat`
3. Wait for automated setup to complete
4. Start chatting with Mythic!

#### Option 2: PowerShell Script
1. Right-click `start_mythic.ps1` and select "Run with PowerShell"
2. Wait for automated setup to complete
3. Start chatting with Mythic!

### Linux/macOS
```bash
# Clone the repository
git clone https://github.com/mythic-lite/mythic-lite.git
cd mythic-lite

# Run automated setup
python scripts/setup_environment.py
```

## 📦 Package Installation

### From PyPI (Coming Soon)
```bash
pip install mythic-lite
```

### From Source
```bash
# Clone and install in development mode
git clone https://github.com/mythic-lite/mythic-lite.git
cd mythic-lite
pip install -e .
```

## 🔧 Manual Installation

### Prerequisites
- Python 3.8 or higher
- At least 8GB RAM (16GB+ recommended)
- Sufficient storage for models (~4-8GB)
- Audio input/output capabilities

### Step-by-Step Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/macOS
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Download Models**
   ```bash
   python -m mythic_lite.scripts.initialize_models
   ```

## 🎯 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Model Configuration
MODEL_DIR=./models
CACHE_DIR=./cache
LOG_LEVEL=INFO

# LLM Settings
LLM_MODEL=llama-2-7b-chat.gguf
LLM_CONTEXT_SIZE=4096
LLM_TEMPERATURE=0.7

# TTS Settings
TTS_VOICE=en_US-amy-low
TTS_SPEED=1.0

# ASR Settings
ASR_MODEL=vosk-model-small-en-us-0.15
```

### Model Directory Structure

```
models/
├── llm/
│   └── llama-2-7b-chat.gguf
├── tts/
│   └── en/
│       └── en_US/
│           └── amy/
│               └── low/
│                   └── model.onnx
└── asr/
    └── vosk-model-small-en-us-0.15/
```

## 🐛 Troubleshooting

### Common Issues

#### Audio Problems
- **No audio output**: Check system audio settings and TTS voice installation
- **No audio input**: Verify microphone permissions and PyAudio installation
- **Windows audio issues**: Install Visual C++ Redistributable

#### Model Download Issues
- **Slow downloads**: Use a VPN or mirror site
- **Corrupted files**: Delete partial downloads and retry
- **Insufficient space**: Ensure at least 8GB free space

#### Python Environment Issues
- **Import errors**: Ensure virtual environment is activated
- **Version conflicts**: Use Python 3.8+ and check dependency versions
- **Permission errors**: Run as administrator (Windows) or use sudo (Linux)

### Getting Help

1. Check the [FAQ](../README.md#faq) section
2. Search existing [GitHub Issues](https://github.com/mythic-lite/mythic-lite/issues)
3. Create a new issue with:
   - Operating system and Python version
   - Error messages and logs
   - Steps to reproduce the problem

## 🔄 Updates

### Updating Mythic-Lite
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinstall in development mode
pip install -e .
```

### Updating Models
```bash
# Update all models
python -m mythic_lite.scripts.initialize_models --update

# Update specific model types
python -m mythic_lite.scripts.initialize_models --llm-only
python -m mythic_lite.scripts.initialize_models --tts-only
python -m mythic_lite.scripts.initialize_models --asr-only
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 8GB
- **Storage**: 4GB free space
- **Audio**: Microphone and speakers/headphones

### Recommended Requirements
- **OS**: Windows 11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.10 or higher
- **RAM**: 16GB or more
- **Storage**: 8GB free space
- **Audio**: High-quality microphone and audio output
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster LLM inference)

## 🔒 Security Considerations

- **Local Processing**: All AI processing happens on your device
- **No Data Collection**: No conversation data is sent to external servers
- **Model Verification**: Download models from trusted sources only
- **Environment Isolation**: Use virtual environments to avoid conflicts