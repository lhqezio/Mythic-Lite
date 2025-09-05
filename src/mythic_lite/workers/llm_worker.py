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
            
            # Initialize model with configuration using from_pretrained
            if not model_path.exists():
                raise Exception(f"Model file not found: {model_path}")
            
            self.llm = Llama.from_pretrained(
                repo_id=self.config.llm.model_repo,
                filename=self.config.llm.model_filename,
                verbose=self.config.debug_mode,
                n_ctx=self.config.llm.context_window,
                logits_all=False,
                embedding=False
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
            
            # Use create_chat_completion with optimized chat format for better token efficiency
            response = self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                top_p=0.92,  # Increased for more creative responses
                top_k=45,    # Balanced for engaging but focused responses
                repeat_penalty=1.1,  # Added to prevent repetitive responses
                stop=["</s>", "<|end|>", "\n\n", "Mythic:", "User:"]  # Natural breakpoints for lore sharing
            )
            
            full_response = ""
            token_count = 0
            
            for chunk in response:
                if isinstance(chunk, dict) and 'choices' in chunk:
                    choice = chunk['choices'][0]
                    if 'delta' in choice and 'content' in choice['delta']:
                        token = choice['delta']['content']
                        if token:
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

    def generate_response(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a single response without streaming.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated response text
        """
        if not self.is_initialized or not self.llm:
            error_msg = "LLM not initialized"
            self.logger.error(error_msg)
            return error_msg
        
        max_tokens = max_tokens or self.config.llm.max_tokens
        temperature = temperature or self.config.llm.temperature
        
        start_time = time.time()
        
        try:
            self.logger.debug(f"Generating response with max_tokens={max_tokens}, temperature={temperature}")
            
            # Simplified stop tokens to prevent early stopping
            simple_stop_tokens = ["</s>", "<|end|>", "\n\n"]
            
            response = self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,  # Non-streaming
                top_p=0.92,
                top_k=45,
                repeat_penalty=1.2,  # Increased from 1.1 to prevent repetition
                stop=simple_stop_tokens  # Use simpler stop tokens to prevent early stopping
            )
            
            # Extract the response content
            if response and 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                
                # Validate response quality - prevent repetitive responses
                if self._is_repetitive_response(content):
                    self.logger.warning("Detected repetitive response, regenerating...")
                    # Try one more time with different parameters
                    response = self.llm.create_chat_completion(
                        messages=[
                            {
                                "role": "user",
                                "content": prompt + "\n\nPlease provide a fresh, unique response."
                            }
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature + 0.1,  # Slightly higher temperature
                        stream=False,
                        top_p=0.95,  # Slightly higher top_p
                        top_k=50,    # Slightly higher top_k
                        repeat_penalty=1.3,  # Higher repeat penalty
                        stop=enhanced_stop_tokens
                    )
                    
                    if response and 'choices' in response and len(response['choices']) > 0:
                        content = response['choices'][0]['message']['content']
                
                # Update performance metrics
                token_count = self.estimate_token_count(content)
                response_time = time.time() - start_time
                self._update_performance_metrics(token_count, response_time)
                
                self.logger.debug(f"Generated {token_count} tokens in {response_time:.2f}s")
                return content
            else:
                # Better debugging for failed responses
                self.logger.warning(f"LLM response structure unexpected: {response}")
                if response:
                    self.logger.debug(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
                    if 'choices' in response:
                        self.logger.debug(f"Choices length: {len(response['choices'])}")
                        if response['choices']:
                            self.logger.debug(f"First choice: {response['choices'][0]}")
                
                # Try to extract content even if structure is unexpected
                if response and isinstance(response, dict):
                    # Try different possible response structures
                    if 'choices' in response and response['choices']:
                        choice = response['choices'][0]
                        if isinstance(choice, dict):
                            if 'message' in choice and 'content' in choice['message']:
                                content = choice['message']['content']
                                self.logger.info(f"Extracted content from unexpected structure: {content[:50]}...")
                                return content
                            elif 'text' in choice:
                                content = choice['text']
                                self.logger.info(f"Extracted text from unexpected structure: {content[:50]}...")
                                return content
                            elif 'content' in choice:
                                content = choice['content']
                                self.logger.info(f"Extracted content directly: {content[:50]}...")
                                return content
                    
                    # Try to find any text content in the response
                    response_str = str(response)
                    if len(response_str) > 20:
                        self.logger.warning(f"Response contains data but no extractable content: {response_str[:100]}...")
                
                return "No response generated"
                        
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            self.logger.debug(f"Response generation error details: {e}", exc_info=True)
            return error_msg
    
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

    def _is_repetitive_response(self, content: str) -> bool:
        """
        Check if response is repetitive or stuck in a loop.
        
        Args:
            content: Response content to check
            
        Returns:
            True if response appears repetitive
        """
        if not content or len(content) < 20:
            return False
        
        # Check for repeated phrases
        content_lower = content.lower()
        
        # Common repetitive patterns
        repetitive_patterns = [
            "blast it all",
            "honestly, darling",
            "bloody hell",
            "by jove",
            "mate",
            "darling"
        ]
        
        # Count occurrences of repetitive patterns
        pattern_count = 0
        for pattern in repetitive_patterns:
            if pattern in content_lower:
                pattern_count += content_lower.count(pattern)
        
        # If we have too many repetitive patterns, flag it
        if pattern_count > 3:
            return True
        
        # Check for repeated sentence structures
        sentences = content.split('.')
        if len(sentences) > 2:
            # Check if first few words of sentences are repeated
            first_words = []
            for sentence in sentences[:3]:
                words = sentence.strip().split()[:3]
                if words:
                    first_words.append(' '.join(words).lower())
            
            # If we have repeated sentence starters, flag it
            if len(set(first_words)) < len(first_words):
                return True
        
        return False
