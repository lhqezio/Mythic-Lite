# Mythic-Lite Examples

This directory contains comprehensive examples demonstrating the various features and capabilities of the Mythic-Lite AI chatbot system.

## 📚 Example Files

### 01_basic_usage.py
**Basic Usage Example**
- Demonstrates fundamental system usage
- Shows how to initialize the orchestrator
- Basic conversation handling
- System status and performance statistics

```bash
python examples/01_basic_usage.py
```

### 02_character_system.py
**Character System Example**
- Shows how to use the character system
- Demonstrates the Mythic character (demo)
- Custom character creation
- Character comparison

```bash
python examples/02_character_system.py
```

### 03_llm_abstraction.py
**LLM Abstraction Example**
- Demonstrates the LLM factory
- Custom LLM configuration
- Model validation
- Streaming responses

```bash
python examples/03_llm_abstraction.py
```

### 04_memory_system.py
**Memory System Example**
- Basic memory functionality
- Memory in conversation context
- Memory management features
- Memory recall and summarization

```bash
python examples/04_memory_system.py
```

### 05_performance_monitoring.py
**Performance Monitoring Example**
- System health monitoring
- Performance tracking
- Worker status monitoring
- Benchmarking functionality

```bash
python examples/05_performance_monitoring.py
```

## 🚀 Quick Start

1. **Ensure you have the system installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run a specific example:**
   ```bash
   python examples/01_basic_usage.py
   ```

3. **Run all examples:**
   ```bash
   for example in examples/*.py; do
       echo "Running $example..."
       python "$example"
       echo "Completed $example"
       echo "=================="
   done
   ```

## 📋 Prerequisites

- Python 3.8+
- Mythic-Lite system installed
- Required model files (for LLM functionality)
- Sufficient system resources

## 🎯 What Each Example Demonstrates

### Basic Usage
- System initialization
- Simple conversation handling
- Performance monitoring
- Error handling

### Character System
- Built-in character (Mythic)
- Custom character creation
- Character personality configuration
- Character switching

### LLM Abstraction
- Model factory usage
- Configuration validation
- Different model types
- Streaming responses

### Memory System
- Conversation memory storage
- Memory recall and relevance
- Memory management
- Performance tracking

### Performance Monitoring
- System health checks
- Performance metrics
- Worker status monitoring
- Benchmarking

## 🔧 Configuration

Examples use default configurations that can be customized:

```python
from mythic_lite.core import create_generic_config

# Create custom configuration
config = create_generic_config()
config.llm.max_tokens = 200
config.memory.enable_memory = True
config.system.debug_mode = True
```

## 📊 Expected Output

Each example provides:
- Clear progress indicators
- Success/failure status
- Performance metrics
- Error messages (if any)

## 🐛 Troubleshooting

If examples fail:

1. **Check system requirements:**
   - Python version
   - Required dependencies
   - Model files

2. **Verify configuration:**
   - Model paths
   - API keys (if using external services)
   - System resources

3. **Check logs:**
   - Enable debug mode
   - Review error messages
   - Check system status

## 📖 Learning Path

Recommended order for learning:

1. **01_basic_usage.py** - Start here to understand fundamentals
2. **02_character_system.py** - Learn about character features
3. **03_llm_abstraction.py** - Understand model management
4. **04_memory_system.py** - Explore memory capabilities
5. **05_performance_monitoring.py** - Master monitoring features

## 🤝 Contributing

To add new examples:

1. Follow the naming convention: `XX_description.py`
2. Include comprehensive docstrings
3. Add error handling
4. Update this README
5. Test thoroughly

## 📄 License

Examples are provided under the same license as the main project.