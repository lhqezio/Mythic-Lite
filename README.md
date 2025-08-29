# Mythic-Lite

A professional, enterprise-ready AI chatbot system with modular architecture, LLM abstraction, and intelligent conversation management.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns with focused worker components
- **LLM Abstraction**: Easy swapping of different language models without code changes
- **Intelligent Memory**: Persistent conversation memory with intelligent summarization
- **Professional Logging**: Advanced logging system with performance monitoring
- **Type Safety**: Comprehensive type hints and validation throughout
- **Performance Monitoring**: Built-in performance tracking and health checks
- **Thread Safety**: Thread-safe operations for concurrent usage
- **Configuration Management**: Flexible, validated configuration system

## 🏗️ Architecture

```
src/mythic_lite/
├── core/                    # Core system components
│   ├── config.py           # Configuration management
│   ├── chatbot_orchestrator.py  # Worker coordination
│   └── llm/                # LLM abstraction layer
│       ├── base.py         # Base LLM interface
│       ├── llama_cpp.py    # LLaMA CPP implementation
│       └── factory.py      # Model factory
├── workers/                 # Worker components
│   ├── llm_worker.py       # LLM operations
│   ├── memory_worker.py    # Memory management
│   ├── conversation_worker.py  # Conversation logic
│   ├── tts_worker.py       # Text-to-speech
│   └── asr_worker.py       # Speech recognition
└── utils/                   # Utilities
    ├── logger.py           # Logging system
    ├── cli.py              # Command-line interface
    └── config_manager.py   # Configuration utilities
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/mythic-lite.git
   cd mythic-lite
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies (optional)**
   ```bash
   pip install -r requirements-dev.txt
   ```

## 🎯 Usage

### Basic Usage

```python
from mythic_lite.core import ChatbotOrchestrator, get_config

# Initialize the system
config = get_config()
orchestrator = ChatbotOrchestrator(config)

# Initialize all workers
if orchestrator.initialize_workers():
    # Process user input
    response = orchestrator.process_user_input("Hello, how are you?")
    print(response)
```

### Command Line Interface

```bash
# Start interactive chat
python -m mythic_lite.utils.cli chat

# Check system status
python -m mythic_lite.utils.cli status

# Run benchmarks
python -m mythic_lite.utils.cli benchmark

# Manage configuration
python -m mythic_lite.utils.cli config
```

### Advanced Usage

```python
# Custom configuration
from mythic_lite.core import Config, LLMConfig, ModelType

config = Config()
config.llm = LLMConfig(
    model_type=ModelType.LLAMA_CPP,
    model_path="path/to/model.gguf",
    max_tokens=200,
    temperature=0.8
)

# Initialize with custom config
orchestrator = ChatbotOrchestrator(config)
orchestrator.initialize_workers()

# Streaming response
for token in orchestrator.process_user_input_stream("Tell me a story"):
    print(token, end='', flush=True)
```

## ⚙️ Configuration

The system uses a flexible configuration system with automatic validation:

```python
# Default configuration structure
config = {
    "llm": {
        "model_type": "llama_cpp",
        "max_tokens": 140,
        "temperature": 0.85,
        "context_window": 2048
    },
    "memory": {
        "enable_memory": True,
        "max_memories": 1000,
        "memory_ttl_hours": 168  # 1 week
    },
    "conversation": {
        "system_prompt": "You are Mythic, a 19th century mercenary AI...",
        "max_history_length": 50
    },
    "system": {
        "debug_mode": False,
        "max_workers": 4
    }
}
```

### Environment Variables

```bash
# Set API keys
export ELEVENLABS_API_KEY="your-api-key"

# Enable debug mode
export MYTHIC_DEBUG=1

# Set data directory
export MYTHIC_DATA_DIR="/path/to/data"
```

## 🔧 LLM Abstraction

The system provides a clean abstraction layer for different language models:

```python
from mythic_lite.core.llm import BaseLLM, LLMConfig, ModelType

# LLaMA CPP Model
llama_config = LLMConfig(
    model_type=ModelType.LLAMA_CPP,
    model_path="models/llama-2-7b.gguf",
    max_tokens=140,
    temperature=0.85
)

# Easy to add new model types
class OpenAIModel(BaseLLM):
    def generate_text(self, prompt: str) -> LLMResponse:
        # OpenAI-specific implementation
        pass
```

## 📊 Performance Monitoring

Built-in performance monitoring and health checks:

```python
# Get system health
health = orchestrator.get_system_health()
print(f"System Status: {health['overall_status']}")

# Get performance statistics
stats = orchestrator.get_performance_stats()
print(f"Total Conversations: {stats['total_conversations']}")
print(f"Average Response Time: {stats['average_response_time']:.2f}s")

# Run benchmarks
benchmark = orchestrator.run_benchmark()
print(f"Benchmark Response Time: {benchmark['response_time']:.2f}s")
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage
python -m pytest --cov=src/mythic_lite tests/
```

## 📚 API Reference

### Core Components

- **`ChatbotOrchestrator`**: Main orchestrator for coordinating workers
- **`Config`**: Configuration management with validation
- **`BaseLLM`**: Abstract base class for language models
- **`LLMFactory`**: Factory for creating model instances

### Workers

- **`LLMWorker`**: Handles language model operations
- **`MemoryWorker`**: Manages conversation memory
- **`ConversationWorker`**: Handles conversation logic
- **`TTSWorker`**: Text-to-speech operations
- **`ASRWorker`**: Speech recognition

### Utilities

- **`get_logger()`**: Get logger with performance monitoring
- **`logged_operation()`**: Context manager for operation logging
- **`get_config()`**: Get global configuration instance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
pre-commit run --all-files
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory for detailed documentation
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions

## 🏆 Acknowledgments

- Built with modern Python best practices
- Inspired by professional chatbot architectures
- Designed for enterprise-grade reliability and performance
