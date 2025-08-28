"""
Worker components for Mythic-Lite AI chatbot system.

This module contains specialized workers for different AI tasks:
- ASR (Automatic Speech Recognition)
- LLM (Large Language Model)
- TTS (Text-to-Speech)
- Summarization
"""

# Use lazy imports to avoid circular dependencies
def get_workers():
    """Get all worker classes (lazy import to avoid circular dependencies)."""
    from .asr_worker import ASRWorker
    from .llm_worker import LLMWorker
    from .summarization_worker import SummarizationWorker
    from .tts_worker import TTSWorker
    return ASRWorker, LLMWorker, SummarizationWorker, TTSWorker

def get_asr_worker():
    """Get ASR worker class."""
    from .asr_worker import ASRWorker
    return ASRWorker

def get_llm_worker():
    """Get LLM worker class."""
    from .llm_worker import LLMWorker
    return LLMWorker

def get_summarization_worker():
    """Get summarization worker class."""
    from .summarization_worker import SummarizationWorker
    return SummarizationWorker

def get_tts_worker():
    """Get TTS worker class."""
    from .tts_worker import TTSWorker
    return TTSWorker

__all__ = [
    'get_workers',
    'get_asr_worker',
    'get_llm_worker', 
    'get_summarization_worker',
    'get_tts_worker'
]