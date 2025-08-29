# Mythic-Lite

A professional, enterprise-ready AI chatbot system with modular architecture, LLM abstraction, intelligent conversation management, and a flexible character system.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns with focused worker components
- **LLM Abstraction**: Easy swapping of different language models without code changes
- **Character System**: Flexible character definitions with personality management
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
│   ├── character.py         # Character system
│   ├── demo_config.py       # Demo configurations
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

### Character System

```python
from mythic_lite.core import (
    ChatbotOrchestrator,
    create_mythic_demo_config,
    create_generic_config,
    create_custom_character_config,
    create_custom_character
)

# Use Mythic character (demo)
config = create_mythic_demo_config()
orchestrator = ChatbotOrchestrator(config)

# Use generic assistant
config = create_generic_config()
orchestrator = ChatbotOrchestrator(config)

# Create custom character
custom_character = create_custom_character(
    name="Sage",
    description="A wise philosophical mentor",
    personality_traits=["Wise", "Contemplative", "Patient"],
    formality_level=8,
    empathy_level=9
)

# Use custom character
config = create_custom_character_config("sage")
orchestrator = ChatbotOrchestrator(config)
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

### Character Demo

```bash
# Run character system demo
python examples/02_character_system.py

# Run simple demo
python demo.py
```

### All Examples

```bash
# Run all examples
python examples/01_basic_usage.py      # Basic usage
python examples/02_character_system.py # Character system
python examples/03_llm_abstraction.py  # LLM abstraction
python examples/04_memory_system.py    # Memory system
python examples/05_performance_monitoring.py # Performance monitoring
```

See the [examples/README.md](examples/README.md) for detailed information about each example.

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
        "character_name": "mythic",  # Character to use
        "max_history_length": 50,
        "enable_streaming": True
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

## 🎭 Character System

The system includes a flexible character system that allows you to:

### Built-in Characters

- **Mythic**: A 19th century mercenary AI (demo character)
- **Generic Assistant**: Standard AI assistant

### Custom Characters

```python
from mythic_lite.core import create_custom_character, CharacterManager

# Create a custom character
character_manager = CharacterManager()
custom_character = character_manager.create_custom_character(
    name="Sage",
    description="A wise philosophical mentor",
    personality_traits=["Wise", "Contemplative", "Patient"],
    speech_patterns=["Uses metaphors", "Speaks thoughtfully"],
    interests=["Philosophy", "Personal growth"],
    formality_level=8,
    empathy_level=9
)

# Add to character manager
character_manager.add_character("sage", custom_character)
```

### Character Configuration

```python
# Character personality traits
personality = CharacterPersonality(
    name="Your Character",
    description="Character description",
    background="Character background story",
    personality_traits=["Trait 1", "Trait 2"],
    speech_patterns=["Pattern 1", "Pattern 2"],
    interests=["Interest 1", "Interest 2"],
    formality_level=5,      # 1-10 scale
    humor_level=5,          # 1-10 scale
    assertiveness=7,        # 1-10 scale
    empathy_level=6,        # 1-10 scale
    greeting_style="direct",
    farewell_style="practical",
    question_style="straightforward"
)
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

### Character System

- **`CharacterConfig`**: Character configuration and settings
- **`CharacterPersonality`**: Character personality traits
- **`CharacterManager`**: Manager for character configurations
- **`get_character()`**: Get character by name
- **`create_custom_character()`**: Create custom character

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
- Character system designed for flexibility and extensibility
