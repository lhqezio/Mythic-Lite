"""
Core module for Mythic-Lite chatbot system.

Provides the main configuration, orchestration, and LLM abstraction components.
"""

from .config import (
    get_config, 
    set_config, 
    load_config_from_file, 
    save_config_to_file, 
    reset_config,
    Config,
    LogLevel,
    LoggingConfig,
    LLMConfig,
    TTSConfig,
    ASRConfig,
    MemoryConfig,
    ConversationConfig,
    SystemConfig
)

from .chatbot_orchestrator import ChatbotOrchestrator

from .llm import (
    BaseLLM,
    LLMConfig as LLMConfigBase,
    LLMResponse,
    ChatMessage,
    ModelType
)

from .llm.factory import (
    get_llm_factory,
    create_model,
    create_llama_cpp_model,
    validate_config,
    get_available_models
)

__all__ = [
    # Configuration
    'get_config',
    'set_config', 
    'load_config_from_file',
    'save_config_to_file',
    'reset_config',
    'Config',
    'LogLevel',
    'LoggingConfig',
    'LLMConfig',
    'TTSConfig',
    'ASRConfig',
    'MemoryConfig',
    'ConversationConfig',
    'SystemConfig',
    
    # Orchestration
    'ChatbotOrchestrator',
    
    # LLM Abstraction
    'BaseLLM',
    'LLMConfigBase',
    'LLMResponse',
    'ChatMessage',
    'ModelType',
    
    # LLM Factory
    'get_llm_factory',
    'create_model',
    'create_llama_cpp_model',
    'validate_config',
    'get_available_models'
]