"""
Base LLM interface for Mythic-Lite chatbot system.

Defines the contract that all language model implementations must follow,
enabling easy swapping of different models without changing application logic.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Generator, Union
from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    """Supported model types."""
    LLAMA_CPP = "llama_cpp"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """Configuration for language models."""
    model_type: ModelType
    model_path: Optional[str] = None
    model_repo: Optional[str] = None
    model_filename: Optional[str] = None
    
    # Generation parameters
    max_tokens: int = 140
    temperature: float = 0.85
    context_window: int = 2048
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    
    # Model-specific settings
    n_gpu_layers: int = 0
    n_threads: int = 4
    verbose: bool = False
    
    # API settings (for cloud models)
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None


@dataclass
class LLMResponse:
    """Standardized response from language models."""
    text: str
    tokens_generated: int
    response_time: float
    model_name: str
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatMessage:
    """Standardized chat message format."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLM(ABC):
    """Abstract base class for all language model implementations."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model_name = self._get_model_name()
        self.is_initialized = False
        self.initialization_error: Optional[str] = None
        
        # Performance tracking
        self.total_requests = 0
        self.total_tokens_generated = 0
        self.average_response_time = 0.0
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the language model."""
        pass
    
    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def generate_text_stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Generator[LLMResponse, None, None]:
        """Generate text from a prompt with streaming."""
        pass
    
    @abstractmethod
    def generate_chat(
        self, 
        messages: List[ChatMessage], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from chat messages."""
        pass
    
    @abstractmethod
    def generate_chat_stream(
        self, 
        messages: List[ChatMessage], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Generator[LLMResponse, None, None]:
        """Generate response from chat messages with streaming."""
        pass
    
    def _get_model_name(self) -> str:
        """Get a human-readable model name."""
        if self.config.model_path:
            return f"{self.config.model_type.value}_{self.config.model_path}"
        elif self.config.model_repo:
            return f"{self.config.model_type.value}_{self.config.model_repo}"
        else:
            return f"{self.config.model_type.value}_unknown"
    
    def _update_performance_metrics(self, tokens: int, response_time: float):
        """Update performance tracking metrics."""
        self.total_requests += 1
        self.total_tokens_generated += tokens
        
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the LLM."""
        return {
            'model_name': self.model_name,
            'model_type': self.config.model_type.value,
            'initialized': self.is_initialized,
            'error': self.initialization_error,
            'total_requests': self.total_requests,
            'total_tokens_generated': self.total_tokens_generated,
            'average_response_time': self.average_response_time,
            'config': {
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'context_window': self.config.context_window
            }
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'total_requests': self.total_requests,
            'total_tokens_generated': self.total_tokens_generated,
            'average_response_time': self.average_response_time,
            'tokens_per_second': (
                self.total_tokens_generated / self.average_response_time 
                if self.average_response_time > 0 else 0
            )
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_initialized = False
        self.initialization_error = None
    
    def is_available(self) -> bool:
        """Check if the LLM is available for use."""
        return self.is_initialized and not self.initialization_error
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields based on model type
        if self.config.model_type == ModelType.LLAMA_CPP:
            if not self.config.model_path and not self.config.model_repo:
                validation['errors'].append("LLaMA CPP model requires model_path or model_repo")
                validation['valid'] = False
        
        # Check parameter ranges
        if self.config.temperature < 0.0 or self.config.temperature > 2.0:
            validation['warnings'].append("Temperature should be between 0.0 and 2.0")
        
        if self.config.max_tokens <= 0:
            validation['errors'].append("Max tokens must be positive")
            validation['valid'] = False
        
        if self.config.context_window <= 0:
            validation['errors'].append("Context window must be positive")
            validation['valid'] = False
        
        return validation