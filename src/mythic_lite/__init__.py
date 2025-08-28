"""
Mythic-Lite: A lightweight, local AI chatbot system with text-to-speech capabilities.

A privacy-conscious AI chatbot that runs entirely on local hardware with:
- Local AI processing using LLM models
- Text-to-speech synthesis
- Speech recognition
- Conversation memory and management
- Beautiful CLI interface
"""

__version__ = "0.1.0"
__author__ = "Mythic-Lite Team"
__description__ = "A lightweight, local AI chatbot system with text-to-speech capabilities"

# Import core components (these don't have circular dependencies)
from .core import Config, ConversationWorker, ModelManager

# Import utilities (these don't have circular dependencies)
from .utils import Logger, WindowsInput

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__description__',
    
    # Core components (no circular dependencies)
    'Config',
    'ConversationWorker',
    'ModelManager',
    
    # Utils (no circular dependencies)
    'Logger',
    'WindowsInput',
]

# Lazy imports to avoid circular dependencies
def get_chatbot_orchestrator():
    """Get the ChatbotOrchestrator class (lazy import to avoid circular dependencies)."""
    from .core import get_chatbot_orchestrator
    return get_chatbot_orchestrator()

def get_workers():
    """Get worker classes (lazy import to avoid circular dependencies)."""
    from .workers import get_workers
    return get_workers()

def get_cli():
    """Get the CLI class (lazy import to avoid circular dependencies)."""
    from .utils import get_cli
    return get_cli()

# Convenience functions for backward compatibility
def get_asr_worker():
    """Get ASR worker class."""
    from .workers import get_asr_worker
    return get_asr_worker()

def get_llm_worker():
    """Get LLM worker class."""
    from .workers import get_llm_worker
    return get_llm_worker()

def get_summarization_worker():
    """Get summarization worker class."""
    from .workers import get_summarization_worker
    return get_summarization_worker()

def get_tts_worker():
    """Get TTS worker class."""
    from .workers import get_tts_worker
    return get_tts_worker()
