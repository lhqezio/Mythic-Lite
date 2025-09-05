# Mythic-Lite

## 🪄 What is Mythic? (the non-boring version)

Mythic is my playground for weird AI ideas.  
Think: Roblox clowns, cursed TikTok experiments, and NPCs with emotional damage.  

Yes, it’s half-baked. But half-baked on purpose.  
Runs locally, talks back, and might roast you if you let it.  

Right now it’s roleplaying as a 19th-century mercenary who talks funny.

## 🚀 Features

- **Local AI Processing**: Run completely offline using local LLM models
- **Text-to-Speech**: Natural voice synthesis with customizable voices
- **Speech Recognition**: Lightweight offline ASR system using Vosk for voice input
- **Conversation Memory**: Intelligent conversation management with automatic summarization
- **Beautiful CLI Interface**: Modern, intuitive command-line interface with rich output
- **Modular Architecture**: Separate workers for LLM, TTS, ASR, and summarization tasks
- **Rich Logging**: Comprehensive logging with configurable output formats
- **Environment Configuration**: Flexible configuration via environment variables
- **Automated Setup**: One-click environment setup with virtual environment and dependencies

## 🏗️ Architecture

Mythic-Lite uses a modular architecture with specialized workers:

- **Chatbot Orchestrator**: Coordinates all components and manages conversation flow
- **LLM Worker**: Handles language model inference and text generation
- **TTS Worker**: Manages text-to-speech synthesis
- **ASR Worker**: Handles automatic speech recognition for voice input
- **Summarization Worker**: Handles conversation summarization for memory management
- **Conversation Worker**: Manages conversation state and memory

## 📋 Requirements

- Python 3.8+
- Windows 10/11, Linux (Ubuntu 18.04+), or macOS 10.15+
- At least 8GB RAM (16GB+ recommended)
- Sufficient storage for model files (~4-8GB)
- Audio input/output capabilities

## 🛠️ Installation

### Option 1: Automated Setup (Recommended)

#### Windows
1. **Download the project** and navigate to the `scripts` folder
2. **Double-click** `start_mythic.bat` (easiest) or run `start_mythic.ps1` with PowerShell
3. **Wait** for the automated setup to complete
4. **Enjoy** your conversation with Mythic!

#### Linux/macOS
```bash
# Clone the repository
git clone <repository-url>
cd Mythic-Lite

# Run the automated installation script
./scripts/install.sh
```

### Option 2: Package Installation

```bash
# Install from source (development mode)
git clone <repository-url>
cd Mythic-Lite
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### Option 3: Manual Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Mythic-Lite
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Unix/Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Download required models**:
   ```bash
   python -m mythic_lite.scripts.initialize_models
   ```

## 🚀 Quick Start

### Using the CLI
```bash
# Start the chatbot
python -m mythic_lite.utils.cli

# Or use the startup script
./start_mythic.sh  # Linux/macOS
start_mythic.bat   # Windows
```

### Programmatic Usage
```python
from mythic_lite import ChatbotOrchestrator, Config, Logger

# Initialize the system
config = Config()
logger = Logger(config)
orchestrator = ChatbotOrchestrator(config, logger)

# Start a conversation
await orchestrator.initialize()
response = await orchestrator.process_input("Hello, how are you?")
print(f"Mythic: {response}")
```

See [examples/basic_usage.py](examples/basic_usage.py) for a complete example.

## 📁 Project Structure

```
mythic-lite/
├── src/mythic_lite/          # Main package source code
│   ├── core/                 # Core components (orchestrator, config, etc.)
│   ├── workers/              # Specialized AI workers (LLM, TTS, ASR, etc.)
│   ├── utils/                # Utilities (CLI, logging, etc.)
│   └── scripts/              # Setup and utility scripts
├── tests/                    # Test suite
├── docs/                     # Documentation
├── examples/                 # Usage examples
├── scripts/                  # Installation and startup scripts
├── pyproject.toml           # Modern Python packaging configuration
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md                # This file
```

## 🔧 Configuration

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
├── llm/                     # Language models
├── tts/                     # Text-to-speech voices
└── asr/                     # Speech recognition models
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mythic_lite --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Examples](examples/)** - Usage examples and tutorials
