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
