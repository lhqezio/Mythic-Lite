"""
Demo configuration for Mythic-Lite chatbot system.

Provides a demo configuration that uses the Mythic character
as an example of the character system.
"""

from .config import Config, ConversationConfig
from .character import get_character


def create_mythic_demo_config() -> Config:
    """Create a demo configuration using the Mythic character."""
    config = Config()
    
    # Set up conversation to use Mythic character
    config.conversation.character_name = "mythic"
    
    # Update system settings for demo
    config.system.debug_mode = False
    config.system.enable_benchmarks = True
    
    # Optimize for demo performance
    config.llm.max_tokens = 150
    config.llm.temperature = 0.8
    config.conversation.max_history_length = 30
    
    return config


def create_generic_config() -> Config:
    """Create a generic configuration without any specific character."""
    config = Config()
    
    # Use default conversation settings
    config.conversation.character_name = None
    config.conversation.system_prompt = "You are a helpful AI assistant. Be direct, practical, and maintain a professional tone."
    config.conversation.user_prefix = "User: "
    config.conversation.assistant_prefix = "Assistant: "
    
    return config


def create_custom_character_config(character_name: str, **kwargs) -> Config:
    """Create a configuration using a custom character."""
    config = Config()
    
    # Set up conversation to use custom character
    config.conversation.character_name = character_name
    
    # Apply any additional settings
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config