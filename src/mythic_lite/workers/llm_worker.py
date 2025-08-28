"""
LLM Worker module for Mythic-Lite chatbot system.
Handles the main language model for conversation generation.
"""

import threading
import time
from typing import Generator, Tuple, Optional, Dict, Any
from llama_cpp import Llama

# Use lazy imports to avoid circular dependencies
def get_core_modules():
    """Get core modules when needed."""
    from ..core.config import get_config
    from ..core.model_manager import ensure_model
    return get_config, ensure_model

from ..utils.logger import get_logger


class LLMWorker:
    """Worker class for handling the main LLM conversation model."""
    
    def __init__(self, config: Optional[Any] = None):
        # Get core modules when needed
        get_config, ensure_model = get_core_modules()
        
        self.config = config or get_config()
        self.logger = get_logger("llm-worker")
        
        self.llm: Optional[Llama] = None
        self.is_initialized: bool = False
        self.initialization_error: Optional[str] = None
        
        # Performance tracking
        self.total_requests: int = 0
        self.total_tokens_generated: int = 0
        self.average_response_time: float = 0.0
        
    def initialize(self) -> bool:
        """Initialize the main LLM model."""
        try:
            self.logger.info("Initializing main LLM model...")
            
            # Get core modules when needed
            get_config, ensure_model = get_core_modules()
            
            # Ensure model is downloaded
            model_path = ensure_model(
                "llm",
                self.config.llm.model_repo,
                self.config.llm.model_filename
            )
            
            if not model_path:
                raise Exception("Failed to download LLM model")
            
            # Initialize model with configuration
            # For local GGUF files, use Llama() directly instead of from_pretrained()
            # model_path already includes the filename, so use it directly
            if not model_path.exists():
                raise Exception(f"Model file not found: {model_path}")
            
            self.llm = Llama(
                model_path=str(model_path),
                verbose=self.config.debug_mode,
                n_ctx=self.config.llm.context_window
            )
            
            self.is_initialized = True
            self.initialization_error = None
            
            self.logger.success("Main LLM model initialized successfully!")
            self.logger.info(f"Model: {self.config.llm.model_repo}")
            self.logger.info(f"Context window: {self.config.llm.context_window} tokens")
            
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.error(f"Failed to initialize main LLM model: {e}")
            self.logger.debug(f"Initialization error details: {e}", exc_info=True)
            return False
    
    def generate_response_stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Generate response using Llama with streaming.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate (uses config default if None)
            temperature: Sampling temperature (uses config default if None)
            
        Yields:
            Tuple of (token, full_response)
        """
        if not self.is_initialized or not self.llm:
            error_msg = "LLM not initialized"
            self.logger.error(error_msg)
            yield error_msg, ""
            return
        
        # Use configuration defaults if not specified
        max_tokens = max_tokens or self.config.llm.max_tokens
        temperature = temperature or self.config.llm.temperature
        
        start_time = time.time()
        
        try:
            self.logger.debug(f"Generating response with max_tokens={max_tokens}, temperature={temperature}")
            
            # Use stream=True for token-by-token generation with specific stop sequences
            stream = self.llm(
                prompt, 
                max_tokens=max_tokens,
                temperature=temperature, 
                stream=True,
                stop=["<|user|>", "<|system|>", "</s>", "<s>"]
            )
            
            full_response = ""
            token_count = 0
            
            for chunk in stream:
                if isinstance(chunk, dict) and 'choices' in chunk:
                    token = chunk['choices'][0].get('text', '')
                    if token:
                        # Check for complete prompt artifacts
                        if any(indicator in token for indicator in ['<|user|', '<|system|', '<|assistant|', '</s>', '<s>']):
                            break
                        full_response += token
                        token_count += 1
                        yield token, full_response
                        
                elif hasattr(chunk, 'choices'):
                    token = chunk.choices[0].text if chunk.choices else ''
                    if token:
                        # Check for complete prompt artifacts
                        if any(indicator in token for indicator in ['<|user|', '<|system|', '<|assistant|', '</s>', '<s>']):
                            break
                        full_response += token
                        token_count += 1
                        yield token, full_response
            
            # Update performance metrics
            response_time = time.time() - start_time
            self._update_performance_metrics(token_count, response_time)
            
            self.logger.debug(f"Generated {token_count} tokens in {response_time:.2f}s")
                        
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            self.logger.debug(f"Response generation error details: {e}", exc_info=True)
            yield error_msg, ""
    
    def estimate_token_count(self, text: str) -> int:
        """
        Rough estimate of token count.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # 4 chars per token is a reasonable approximation for most models
        return len(text) // 4
    
    def check_prompt_length(self, prompt: str) -> int:
        """
        Check if prompt is getting too long for the context window.
        
        Args:
            prompt: Prompt to check
            
        Returns:
            Estimated token count
        """
        estimated_tokens = self.estimate_token_count(prompt)
        max_tokens = self.config.llm.context_window
        
        if estimated_tokens > max_tokens * 0.8:  # 80% of context window
            self.logger.warning(
                f"Prompt is getting long (~{estimated_tokens} tokens). "
                f"Context window: {max_tokens} tokens"
            )
        elif estimated_tokens > max_tokens * 0.6:  # 60% of context window
            self.logger.info(f"Prompt length: ~{estimated_tokens} tokens")
        
        return estimated_tokens
    
    def get_status(self) -> str:
        """Get the status of the LLM worker."""
        if self.is_initialized:
            return f"Main LLM: {self.config.llm.model_repo} (Loaded & Ready)"
        elif self.initialization_error:
            return f"Main LLM: Failed to initialize - {self.initialization_error}"
        else:
            return "Main LLM: Not initialized"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "total_requests": self.total_requests,
            "total_tokens_generated": self.total_tokens_generated,
            "average_response_time": self.average_response_time,
            "is_initialized": self.is_initialized
        }
    
    def _update_performance_metrics(self, tokens_generated: int, response_time: float):
        """Update performance tracking metrics."""
        self.total_requests += 1
        self.total_tokens_generated += tokens_generated
        
        # Update running average
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
    
    def cleanup(self):
        """Clean up resources."""
        if self.llm:
            try:
                # Llama.cpp models don't have explicit cleanup methods
                self.llm = None
                self.is_initialized = False
                self.logger.info("LLM worker cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error during LLM cleanup: {e}")
                self.logger.debug(f"Cleanup error details: {e}", exc_info=True)
        else:
            self.logger.debug("LLM worker already cleaned up")
