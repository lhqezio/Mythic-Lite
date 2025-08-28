# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional package structure with proper organization
- Comprehensive documentation
- Development tools configuration (black, isort, mypy, pytest)
- Cross-platform installation scripts
- Example usage code
- MIT License

### Changed
- Restructured repository into logical modules
- Moved source code to `src/mythic_lite/` package structure
- Organized code into core, workers, utils, and scripts modules
- Updated import paths and package structure

### Fixed
- Package import issues
- Module organization
- Development workflow setup

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Mythic-Lite
- Local AI chatbot system with text-to-speech capabilities
- Speech recognition using Vosk
- Conversation memory and management
- Beautiful CLI interface
- Modular architecture with specialized workers
- Comprehensive logging system
- Environment configuration support
- Automated setup scripts for Windows

### Features
- **Local AI Processing**: Run completely offline using local LLM models
- **Text-to-Speech**: Natural voice synthesis with customizable voices
- **Speech Recognition**: Lightweight offline ASR system
- **Conversation Memory**: Intelligent conversation management with automatic summarization
- **Modular Architecture**: Separate workers for LLM, TTS, ASR, and summarization tasks
- **Rich Logging**: Comprehensive logging with configurable output formats
- **Environment Configuration**: Flexible configuration via environment variables
- **Automated Setup**: One-click environment setup with virtual environment and dependencies

### Technical Details
- Python 3.8+ compatibility
- Cross-platform support (Windows, Linux, macOS)
- Memory-efficient model loading
- Asynchronous processing architecture
- Comprehensive error handling and logging