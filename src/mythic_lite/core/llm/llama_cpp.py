"""
LLaMA CPP implementation for Mythic-Lite chatbot system.

Provides a concrete implementation of the BaseLLM interface
for LLaMA CPP models.
"""

import time
import threading
from typing import Optional, List, Dict, Any, Generator
from pathlib import Path

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    # Mock class for testing
    class Llama:
        def __init__(self, **kwargs):
            pass
        
        def create_completion(self, **kwargs):
            return type('MockResponse', (), {
                'choices': [type('MockChoice', (), {
                    'text': 'Mock response',
                    'finish_reason': 'stop'
                })()],
                'usage': type('MockUsage', (), {
                    'total_tokens': 10
                })()
            })()
        
        def create_chat_completion(self, **kwargs):
            return type('MockResponse', (), {
                'choices': [type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': 'Mock chat response'
                    })()
                })()],
                'usage': type('MockUsage', (), {
                    'total_tokens': 10
                })()
            })()

from .base import BaseLLM, LLMResponse, LLMConfig, ChatMessage, ModelType
from ...utils.logger import get_logger


class LlamaCPPModel(BaseLLM):
    """LLaMA CPP model implementation."""
    
    def __init__(self, config: LLMConfig):
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python is not available")
        
        super().__init__(config)
        self.logger = get_logger("llama-cpp-model")
        self.model: Optional[Llama] = None
        
        # Validate config
        if config.model_type != ModelType.LLAMA_CPP:
            raise ValueError("Config must be for LLaMA CPP model type")
    
    def initialize(self) -> bool:
        """Initialize the LLaMA CPP model."""
        try:
            self.logger.info("Initializing LLaMA CPP model...")
            
            # Determine model path
            model_path = self._get_model_path()
            if not model_path or not model_path.exists():
                raise Exception(f"Model file not found: {model_path}")
            
            # Initialize LLaMA model
            self.model = Llama(
                model_path=str(model_path),
                n_ctx=self.config.context_window,
                n_gpu_layers=self.config.n_gpu_layers,
                n_threads=self.config.n_threads,
                verbose=self.config.verbose,
                logits_all=False,
                embedding=False
            )
            
            self.is_initialized = True
            self.initialization_error = None
            
            self.logger.info(f"LLaMA CPP model initialized successfully: {model_path}")
            self.logger.info(f"Context window: {self.config.context_window} tokens")
            
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.error(f"Failed to initialize LLaMA CPP model: {e}")
            return False
    
    def _get_model_path(self) -> Optional[Path]:
        """Get the path to the model file."""
        if self.config.model_path:
            return Path(self.config.model_path)
        elif self.config.model_repo and self.config.model_filename:
            # This would need to be implemented based on your model management
            # For now, return a default path
            return Path("models") / self.config.model_filename
        else:
            return None
    
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text from a prompt."""
        if not self.is_available():
            raise RuntimeError("LLM model not initialized")
        
        start_time = time.time()
        
        try:
            # Use config defaults if not specified
            max_tokens = max_tokens or self.config.max_tokens
            temperature = temperature or self.config.temperature
            
            # Generate completion
            response = self.model.create_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                repeat_penalty=self.config.repeat_penalty,
                stream=False,
                **kwargs
            )
            
            # Extract response
            text = response.choices[0].text
            tokens_generated = response.usage.total_tokens
            response_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(tokens_generated, response_time)
            
            return LLMResponse(
                text=text,
                tokens_generated=tokens_generated,
                response_time=response_time,
                model_name=self.model_name,
                finish_reason=response.choices[0].finish_reason,
                metadata={'prompt_length': len(prompt)}
            )
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            raise
    
    def generate_text_stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Generator[LLMResponse, None, None]:
        """Generate text from a prompt with streaming."""
        if not self.is_available():
            raise RuntimeError("LLM model not initialized")
        
        start_time = time.time()
        
        try:
            # Use config defaults if not specified
            max_tokens = max_tokens or self.config.max_tokens
            temperature = temperature or self.config.temperature
            
            # Generate streaming completion
            stream = self.model.create_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                repeat_penalty=self.config.repeat_penalty,
                stream=True,
                **kwargs
            )
            
            accumulated_text = ""
            total_tokens = 0
            
            for chunk in stream:
                if chunk.choices[0].delta.text:
                    text_chunk = chunk.choices[0].delta.text
                    accumulated_text += text_chunk
                    total_tokens += 1
                    
                    response_time = time.time() - start_time
                    
                    yield LLMResponse(
                        text=text_chunk,
                        tokens_generated=1,
                        response_time=response_time,
                        model_name=self.model_name,
                        finish_reason=chunk.choices[0].finish_reason,
                        metadata={'is_partial': True, 'accumulated_text': accumulated_text}
                    )
            
            # Final response with complete text
            final_response_time = time.time() - start_time
            self._update_performance_metrics(total_tokens, final_response_time)
            
            yield LLMResponse(
                text=accumulated_text,
                tokens_generated=total_tokens,
                response_time=final_response_time,
                model_name=self.model_name,
                finish_reason='stop',
                metadata={'is_partial': False, 'prompt_length': len(prompt)}
            )
            
        except Exception as e:
            self.logger.error(f"Streaming text generation failed: {e}")
            raise
    
    def generate_chat(
        self, 
        messages: List[ChatMessage], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from chat messages."""
        if not self.is_available():
            raise RuntimeError("LLM model not initialized")
        
        start_time = time.time()
        
        try:
            # Use config defaults if not specified
            max_tokens = max_tokens or self.config.max_tokens
            temperature = temperature or self.config.temperature
            
            # Convert to LLaMA CPP format
            llama_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Generate chat completion
            response = self.model.create_chat_completion(
                messages=llama_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                repeat_penalty=self.config.repeat_penalty,
                stream=False,
                **kwargs
            )
            
            # Extract response
            text = response.choices[0].message.content
            tokens_generated = response.usage.total_tokens
            response_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(tokens_generated, response_time)
            
            return LLMResponse(
                text=text,
                tokens_generated=tokens_generated,
                response_time=response_time,
                model_name=self.model_name,
                finish_reason=response.choices[0].finish_reason,
                metadata={'message_count': len(messages)}
            )
            
        except Exception as e:
            self.logger.error(f"Chat generation failed: {e}")
            raise
    
    def generate_chat_stream(
        self, 
        messages: List[ChatMessage], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Generator[LLMResponse, None, None]:
        """Generate response from chat messages with streaming."""
        if not self.is_available():
            raise RuntimeError("LLM model not initialized")
        
        start_time = time.time()
        
        try:
            # Use config defaults if not specified
            max_tokens = max_tokens or self.config.max_tokens
            temperature = temperature or self.config.temperature
            
            # Convert to LLaMA CPP format
            llama_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Generate streaming chat completion
            stream = self.model.create_chat_completion(
                messages=llama_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                repeat_penalty=self.config.repeat_penalty,
                stream=True,
                **kwargs
            )
            
            accumulated_text = ""
            total_tokens = 0
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text_chunk = chunk.choices[0].delta.content
                    accumulated_text += text_chunk
                    total_tokens += 1
                    
                    response_time = time.time() - start_time
                    
                    yield LLMResponse(
                        text=text_chunk,
                        tokens_generated=1,
                        response_time=response_time,
                        model_name=self.model_name,
                        finish_reason=chunk.choices[0].finish_reason,
                        metadata={'is_partial': True, 'accumulated_text': accumulated_text}
                    )
            
            # Final response with complete text
            final_response_time = time.time() - start_time
            self._update_performance_metrics(total_tokens, final_response_time)
            
            yield LLMResponse(
                text=accumulated_text,
                tokens_generated=total_tokens,
                response_time=final_response_time,
                model_name=self.model_name,
                finish_reason='stop',
                metadata={'is_partial': False, 'message_count': len(messages)}
            )
            
        except Exception as e:
            self.logger.error(f"Streaming chat generation failed: {e}")
            raise
    
    def cleanup(self):
        """Cleanup LLaMA CPP model resources."""
        super().cleanup()
        
        if self.model:
            # LLaMA CPP models don't have explicit cleanup
            self.model = None
        
        self.logger.info("LLaMA CPP model cleaned up")