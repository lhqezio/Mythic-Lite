"""
Core components for Mythic-Lite AI chatbot system.

This module contains the main orchestration, conversation management,
model management, and configuration components.
"""

from .config import get_config, Config
from .conversation_worker import ConversationWorker
from .model_manager import ModelManager

# Use lazy imports to avoid circular dependencies
def get_chatbot_orchestrator():
    """Get the ChatbotOrchestrator class (lazy import to avoid circular dependencies)."""
    from .chatbot_orchestrator import ChatbotOrchestrator
    return ChatbotOrchestrator

__all__ = [
    'get_config',
    'Config',
    'ConversationWorker', 
    'ModelManager',
    'get_chatbot_orchestrator'
]