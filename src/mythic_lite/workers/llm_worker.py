"""
LLM Worker module for Mythic-Lite chatbot system.

Handles language model operations using the new abstraction layer,
enabling easy swapping of different model types.
"""

import time
from typing import Generator, Tuple, Optional, Dict, Any, List
from pathlib import Path

from ..core.llm import BaseLLM, LLMConfig, ModelType, ChatMessage, LLMResponse
from ..core.llm.factory import get_llm_factory
from ..utils.logger import get_logger


class LLMWorker:
    """Worker class for handling language model operations."""
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.logger = get_logger("llm-worker")
        
        # LLM instance using abstraction layer
        self.llm: Optional[BaseLLM] = None
        self.is_initialized: bool = False
        self.initialization_error: Optional[str] = None
        
        # Factory for creating models
        self.factory = get_llm_factory()
        
        # Performance tracking
        self.total_requests: int = 0
        self.total_tokens_generated: int = 0
        self.average_response_time: float = 0.0
        
    def initialize(self) -> bool:
        """Initialize the language model using the abstraction layer."""
        try:
            self.logger.info("Initializing language model...")
            
            # Create LLM configuration
            llm_config = self._create_llm_config()
            
            # Validate configuration
            validation = self.factory.validate_model_config(llm_config)
            if not validation['valid']:
                errors = ', '.join(validation['errors'])
                raise Exception(f"Invalid LLM configuration: {errors}")
            
            # Create model instance
            self.llm = self.factory.create_model(llm_config)
            
            # Initialize the model
            if not self.llm.initialize():
                raise Exception("Failed to initialize language model")
            
            self.is_initialized = True
            self.initialization_error = None
            
            self.logger.success("Language model initialized successfully!")
            self.logger.info(f"Model: {self.llm.model_name}")
            self.logger.info(f"Type: {self.llm.config.model_type.value}")
            
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.error(f"Failed to initialize language model: {e}")
            return False
    
    def _create_llm_config(self) -> LLMConfig:
        """Create LLM configuration from the main config."""
        try:
            # Extract LLM settings from main config
            llm_settings = self.config.llm if hasattr(self.config, 'llm') else {}
            
            # Create LLM configuration
            config = LLMConfig(
                model_type=ModelType.LLAMA_CPP,  # Default to LLaMA CPP
                model_repo=llm_settings.get('model_repo'),
                model_filename=llm_settings.get('model_filename'),
                max_tokens=llm_settings.get('max_tokens', 140),
                temperature=llm_settings.get('temperature', 0.85),
                context_window=llm_settings.get('context_window', 2048),
                top_p=llm_settings.get('top_p', 0.9),
                top_k=llm_settings.get('top_k', 40),
                repeat_penalty=llm_settings.get('repeat_penalty', 1.1),
                n_gpu_layers=llm_settings.get('n_gpu_layers', 0),
                n_threads=llm_settings.get('n_threads', 4),
                verbose=getattr(self.config, 'debug_mode', False)
            )
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to create LLM config: {e}")
            # Return default config as fallback
            return self.factory.get_default_config()
    
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """Generate a response from a prompt."""
        if not self.is_available():
            self.logger.error("Language model not available")
            return None
        
        try:
            response = self.llm.generate_text(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Update performance metrics
            self._update_performance_metrics(response.tokens_generated, response.response_time)
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return None
    
    def generate_response_stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Generate response using streaming.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate (uses config default if None)
            temperature: Sampling temperature (uses config default if None)
            
        Yields:
            Tuple of (token, full_response_so_far)
        """
        if not self.is_available():
            self.logger.error("Language model not available")
            return
        
        try:
            accumulated_text = ""
            
            for response in self.llm.generate_text_stream(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                if response.text:
                    accumulated_text += response.text
                    yield response.text, accumulated_text
            
            # Update performance metrics with final response
            if hasattr(response, 'tokens_generated') and hasattr(response, 'response_time'):
                self._update_performance_metrics(response.tokens_generated, response.response_time)
            
        except Exception as e:
            self.logger.error(f"Failed to generate streaming response: {e}")
    
    def generate_chat_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """Generate a response from chat messages."""
        if not self.is_available():
            self.logger.error("Language model not available")
            return None
        
        try:
            # Convert to ChatMessage format
            chat_messages = [
                ChatMessage(role=msg['role'], content=msg['content'])
                for msg in messages
            ]
            
            response = self.llm.generate_chat(
                messages=chat_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Update performance metrics
            self._update_performance_metrics(response.tokens_generated, response.response_time)
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Failed to generate chat response: {e}")
            return None
    
    def generate_chat_response_stream(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Generator[Tuple[str, str], None, None]:
        """Generate chat response using streaming."""
        if not self.is_available():
            self.logger.error("Language model not available")
            return
        
        try:
            # Convert to ChatMessage format
            chat_messages = [
                ChatMessage(role=msg['role'], content=msg['content'])
                for msg in messages
            ]
            
            accumulated_text = ""
            
            for response in self.llm.generate_chat_stream(
                messages=chat_messages,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                if response.text:
                    accumulated_text += response.text
                    yield response.text, accumulated_text
            
            # Update performance metrics with final response
            if hasattr(response, 'tokens_generated') and hasattr(response, 'response_time'):
                self._update_performance_metrics(response.tokens_generated, response.response_time)
            
        except Exception as e:
            self.logger.error(f"Failed to generate streaming chat response: {e}")
    
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
    
    def get_status(self) -> str:
        """Get the status of the LLM worker."""
        if not self.llm:
            return "LLM: Not initialized"
        
        return f"LLM: {self.llm.model_name} ({self.llm.config.model_type.value})"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'total_requests': self.total_requests,
            'total_tokens_generated': self.total_tokens_generated,
            'average_response_time': self.average_response_time
        }
        
        # Add LLM-specific stats if available
        if self.llm:
            stats.update(self.llm.get_performance_stats())
        
        return stats
    
    def is_available(self) -> bool:
        """Check if the LLM is available for use."""
        return self.is_initialized and self.llm and self.llm.is_available()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.llm:
            return {'error': 'No model loaded'}
        
        return {
            'name': self.llm.model_name,
            'type': self.llm.config.model_type.value,
            'config': {
                'max_tokens': self.llm.config.max_tokens,
                'temperature': self.llm.config.temperature,
                'context_window': self.llm.config.context_window
            },
            'status': self.llm.get_status()
        }
    
    def cleanup(self):
        """Cleanup LLM worker resources."""
        if self.llm:
            self.llm.cleanup()
        
        self.is_initialized = False
        self.initialization_error = None
        self.logger.info("LLM worker cleaned up")
