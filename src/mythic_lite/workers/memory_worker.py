import threading
import time
from typing import Optional, Any, Dict, List

# Remove circular imports - don't import from core
# from .config import get_config
# from .model_manager import ensure_model
from ..utils.logger import get_logger


class MemoryWorker:
    """Worker class for handling conversation memory, summarization, and recall using the main LLM"""
    
    def __init__(self, config: Optional[Any] = None):
        if config is None:
            raise ValueError("Memory worker requires a configuration object. All config must come from the main config file.")
        
        self.config = config
        
        self.logger = get_logger("memory-worker")
        
        # Memory management features
        self.memory_cache = {}  # Cache for quick memory lookups
        self.conversation_patterns = {}  # Track conversation patterns
        self.character_memory = {}  # Remember character-specific details
        
        # LLM reference (will be set by the orchestrator)
        self.llm_worker = None
        
        self.logger.debug("MemoryWorker initialized")
        
    def set_llm_worker(self, llm_worker):
        """Set the LLM worker reference for memory operations."""
        self.llm_worker = llm_worker
        self.is_enabled = llm_worker is not None and llm_worker.is_initialized
        self.logger.debug(f"LLM worker reference set, memory enabled: {self.is_enabled}")
        
    def initialize(self) -> bool:
        """Initialize the memory worker (now just validates LLM worker is available)."""
        try:
            if not self.llm_worker or not self.llm_worker.is_initialized:
                self.logger.warning("LLM worker not available, memory operations will be limited")
                self.is_initialized = False
                self.is_enabled = False
                return False
            
            self.is_initialized = True
            self.is_enabled = True
            self.initialization_error = None
            
            self.logger.success("Memory worker initialized successfully using main LLM!")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.warning(f"Memory worker initialization failed: {e}")
            self.is_initialized = False
            self.is_enabled = False
            return False

    def create_memory_summary(self, text, max_length=100):
        """Create intelligent memory summaries using the main LLM."""
        if not self.is_enabled or not self.llm_worker or not text:
            return None
        
        try:
            # Use configuration settings for memory generation
            max_tokens = getattr(self.config.memory, 'max_tokens', 120)
            temperature = getattr(self.config.memory, 'temperature', 0.1)
            
            # Create a better prompt for memory summarization
            summary_messages = [
                {
                    "role": "system",
                    "content": "You are Mythic, a 19th century mercenary. Summarize this conversation in your own voice, focusing on what the client asked and what you discussed. Be direct and practical. No meta-instructions or explanations about what you're doing."
                },
                {
                    "role": "user",
                    "content": f"Summarize this conversation in {max_length} characters or less:\n\n{text}"
                }
            ]
            
            # Generate summary with timeout protection
            result = [None]
            exception = [None]
            
            def generate_summary():
                try:
                    response = self.llm_worker.llm.create_chat_completion(
                        messages=summary_messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=False
                    )
                    result[0] = response
                except Exception as e:
                    exception[0] = e
            
            # Start generation in separate thread
            summary_thread = threading.Thread(target=generate_summary)
            summary_thread.daemon = True
            summary_thread.start()
            
            # Wait for completion or timeout
            summary_thread.join(timeout=15.0)
            
            if summary_thread.is_alive():
                self.logger.warning("Memory summarization timed out, falling back to simple summary")
                return self._create_simple_memory_summary(text, max_length)
            
            if exception[0]:
                raise exception[0]
            
            # Extract summary from response
            if result[0] and isinstance(result[0], dict) and 'choices' in result[0]:
                summary = result[0]['choices'][0].get('message', {}).get('content', '').strip()
            elif hasattr(result[0], 'choices'):
                summary = result[0].choices[0].message.content.strip() if result[0].choices else ''
            else:
                summary = str(result[0]).strip()
            
            # Clean up the summary - remove any meta-instructions
            summary = summary.replace('Summary:', '').replace('summary:', '').strip()
            summary = summary.replace('Okay, here\'s a memory summary', '').strip()
            summary = summary.replace('aiming for under', '').strip()
            summary = summary.replace('characters', '').strip()
            summary = summary.replace('reflecting a 19th-century mercenary AI\'s perspective:', '').strip()
            summary = summary.replace('as if I were recalling the conversation:', '').strip()
            summary = summary.replace('Write as if you\'re remembering a past conversation.', '').strip()
            
            # Remove quotes and extra formatting
            summary = summary.strip('"').strip("'").strip()
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            # Generate a better memory key
            memory_key = self._generate_memory_key(text)
            
            # Cache this memory for future recall
            if summary and len(summary.strip()) > 5:
                self._cache_memory(memory_key, summary)
                return summary
            return None
            
        except Exception as e:
            self.logger.error(f"Memory summarization failed: {e}")
            return None

    def recall_memory(self, query: str, max_results: int = 3) -> List[str]:
        """Recall relevant memories based on a query."""
        if not self.memory_cache:
            return []
        
        try:
            # Simple keyword-based memory recall
            relevant_memories = []
            query_lower = query.lower()
            
            for key, memory in self.memory_cache.items():
                if any(word in key.lower() or word in memory.lower() for word in query_lower.split()):
                    relevant_memories.append(memory)
            
            # Return top relevant memories
            return relevant_memories[:max_results]
            
        except Exception as e:
            self.logger.error(f"Memory recall failed: {e}")
            return []

    def _cache_memory(self, key: str, memory: str):
        """Cache a memory for future recall."""
        try:
            # Ensure the key is clean and unique
            clean_key = key.strip()
            if not clean_key:
                clean_key = f"memory_{len(self.memory_cache) + 1}_unknown"
            
            # Check if key already exists and make it unique
            if clean_key in self.memory_cache:
                counter = 1
                while f"{clean_key}_{counter}" in self.memory_cache:
                    counter += 1
                clean_key = f"{clean_key}_{counter}"
            
            # Store the memory
            self.memory_cache[clean_key] = memory
            
            # Update memory statistics
            if hasattr(self, 'total_memories'):
                self.total_memories += 1
            else:
                self.total_memories = len(self.memory_cache)
            
            # Limit cache size based on configuration
            max_cache_size = getattr(self.config.memory, 'cache_size', 100)
            if len(self.memory_cache) > max_cache_size:
                # Remove oldest entries (keep the most recent ones)
                oldest_keys = list(self.memory_cache.keys())[:20]
                for old_key in oldest_keys:
                    del self.memory_cache[old_key]
                    
            self.logger.debug(f"Memory cached with key: {clean_key}")
                    
        except Exception as e:
            self.logger.debug(f"Memory caching failed: {e}")

    def _create_simple_memory_summary(self, text: str, max_length: int) -> str:
        """Create a simple memory summary when AI model is not available."""
        try:
            # Extract key information from conversation
            lines = text.split('\n')
            visitor_messages = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Visitor:') or 'visitor' in line.lower():
                    content = line.replace('Visitor:', '').strip()
                    if content and len(content) > 3:
                        visitor_messages.append(content)
            
            if visitor_messages:
                first_message = visitor_messages[0][:40]
                summary = f"Visitor seeking help with: {first_message}"
                
                if len(summary) > max_length:
                    summary = summary[:max_length-3] + "..."
                return summary
            
            return "Conversation memory recorded"
            
        except Exception as e:
            self.logger.debug(f"Simple memory summary failed: {e}")
            return "Memory recorded"

    def create_continuous_memory_summary(self, conversation_text: str, current_summary: str = "", max_length: int = 120) -> str:
        """Create a continuous memory summary that builds upon previous memories using the main LLM."""
        if not self.is_enabled or not self.llm_worker:
            return self._create_simple_memory_summary(conversation_text, max_length)
        
        try:
            # Use configuration settings for memory generation
            max_tokens = getattr(self.config.memory, 'max_tokens', 120)
            temperature = getattr(self.config.memory, 'temperature', 0.1)
            
            # Create incremental memory update
            if current_summary:
                messages = [
                    {
                        "role": "system",
                        "content": f"You are Mythic, a 19th century mercenary AI. Update your existing memory with new conversation developments. Write from your perspective as if you're recalling how a client interaction evolved. Keep the updated memory under {max_length} characters."
                    },
                    {
                        "role": "user",
                        "content": f"Update your existing memory with new conversation content:\n\nYour Previous Memory: {current_summary}\n\nNew Conversation: {conversation_text}\n\nUpdated Memory from your perspective:"
                    }
                ]
            else:
                # First-time memory creation
                messages = [
                    {
                        "role": "system",
                        "content": f"You are Mythic, a 19th century mercenary AI. Create a memory of this conversation as if you're recalling a new client interaction. Focus on key details and the visitor's situation. Keep memories under {max_length} characters."
                    },
                    {
                        "role": "user",
                        "content": f"Create a memory of this conversation:\n\n{conversation_text}"
                    }
                ]
            
            # Generate incremental memory with timeout protection
            result = [None]
            exception = [None]
            
            def generate_memory():
                try:
                    response = self.llm_worker.llm.create_chat_completion(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=False
                    )
                    result[0] = response
                except Exception as e:
                    exception[0] = e
            
            # Start generation in separate thread
            memory_thread = threading.Thread(target=generate_memory)
            memory_thread.daemon = True
            memory_thread.start()
            
            # Wait for completion or timeout
            memory_thread.join(timeout=15.0)
            
            if memory_thread.is_alive():
                self.logger.warning("Continuous memory creation timed out, falling back to simple summary")
                return self._create_simple_memory_summary(conversation_text, max_length)
            
            if exception[0]:
                raise exception[0]
            
            # Extract memory from response
            if result[0] and isinstance(result[0], dict) and 'choices' in result[0]:
                memory = result[0]['choices'][0].get('message', {}).get('content', '').strip()
            elif hasattr(result[0], 'choices'):
                memory = result[0].choices[0].message.content.strip() if result[0].choices else ''
            else:
                memory = str(result[0]).strip()
            
            # Clean up the memory
            memory = memory.replace('Memory:', '').replace('memory:', '').strip()
            
            if len(memory) > max_length:
                memory = memory[:max_length-3] + "..."
            
            # Cache this memory for future recall
            if memory and len(memory.strip()) > 5:
                self._cache_memory(conversation_text[:50], memory)
                return memory
            return None
            
        except Exception as e:
            self.logger.error(f"Continuous memory creation failed: {e}")
            return None

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        return {
            "total_memories": len(self.memory_cache),
            "memory_model_active": self.is_enabled,
            "cache_size": len(self.memory_cache),
            "conversation_patterns": len(self.conversation_patterns),
            "character_memories": len(self.character_memory)
        }

    def clear_memory_cache(self):
        """Clear the memory cache."""
        try:
            self.memory_cache.clear()
            self.conversation_patterns.clear()
            self.character_memory.clear()
            self.logger.info("Memory cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear memory cache: {e}")

    def export_memories(self) -> Dict[str, str]:
        """Export all memories for backup or analysis."""
        try:
            return {
                "conversation_memories": self.memory_cache.copy(),
                "conversation_patterns": self.conversation_patterns.copy(),
                "character_memories": self.character_memory.copy()
            }
        except Exception as e:
            self.logger.error(f"Failed to export memories: {e}")
            return {}

    def import_memories(self, memories: Dict[str, Any]):
        """Import memories from backup or analysis."""
        try:
            if "conversation_memories" in memories:
                self.memory_cache.update(memories["conversation_memories"])
            if "conversation_patterns" in memories:
                self.conversation_patterns.update(memories["conversation_patterns"])
            if "character_memories" in memories:
                self.character_memory.update(memories["character_memories"])
            self.logger.info("Memories imported successfully")
        except Exception as e:
            self.logger.error(f"Failed to import memories: {e}")

    def get_status(self) -> str:
        """Get the status of the memory worker."""
        if self.is_initialized and self.is_enabled:
            return f"Memory: Using Main LLM (AI Memory Active)"
        elif self.is_initialized and not self.is_enabled:
            return f"Memory: Simple Memory Mode (LLM Unavailable)"
        elif self.initialization_error:
            return f"Memory: Failed to initialize - {self.initialization_error}"
        else:
            return "Memory: Not initialized"

    def cleanup(self):
        """Clean up resources"""
        if self.llm_worker:
            try:
                self.llm_worker = None
                self.is_initialized = False
                self.is_enabled = False
                self.logger.info("Memory worker cleaned up")
            except Exception as e:
                self.logger.error(f"Error during memory cleanup: {e}")

    # Backward compatibility methods
    def create_ai_summary(self, text, max_length=100):
        """Backward compatibility method - redirects to create_memory_summary."""
        return self.create_memory_summary(text, max_length)
    
    def create_continuous_summary(self, conversation_text, current_summary="", max_length=120):
        """Backward compatibility method - redirects to create_continuous_memory_summary."""
        return self.create_continuous_memory_summary(conversation_text, current_summary, max_length)
    
    def test_summarization_model(self):
        """Backward compatibility method - tests the memory system using the main LLM."""
        if not self.llm_worker:
            return False
        
        try:
            # Use configuration settings for testing
            max_tokens = getattr(self.config.memory, 'max_tokens', 120)
            temperature = getattr(self.config.memory, 'temperature', 0.1)
            
            # Test prompt using chat format
            test_messages = [
                {
                    "role": "user",
                    "content": "Create a brief memory of this scenario: 'Visitor needs help with a problem.'"
                }
            ]
            
            self.logger.debug(f"[DEBUG] Test messages: {test_messages}")
            
            # Test with timeout protection
            result = [None]
            exception = [None]
            
            def test_model():
                try:
                    self.logger.debug("[DEBUG] Calling main LLM for memory test...")
                    response = self.llm_worker.llm.create_chat_completion(
                        messages=test_messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=False
                    )
                    self.logger.debug(f"[DEBUG] Got test response: {response}")
                    result[0] = response
                except Exception as e:
                    self.logger.debug(f"[DEBUG] Test exception: {e}")
                    exception[0] = e
            
            # Start test in separate thread
            test_thread = threading.Thread(target=test_model)
            test_thread.daemon = True
            test_thread.start()
            
            self.logger.debug("[DEBUG] Test thread started, waiting for response...")
            
            # Wait for completion or timeout
            test_thread.join(timeout=20.0)
            
            if test_thread.is_alive():
                self.logger.warning("Memory model test timed out - model may be slow to start")
                return False
            
            if exception[0]:
                raise exception[0]
            
            self.logger.debug(f"[DEBUG] Test result: {result[0]}")
            
            # Check if we got a valid response
            if result[0]:
                self.logger.debug("[DEBUG] Test passed - got response")
                return True
            else:
                self.logger.debug("[DEBUG] Test failed - no response")
                return False
                
        except Exception as e:
            self.logger.error(f"Memory model test failed: {e}")
            return False

    def _generate_memory_key(self, text: str) -> str:
        """Generate a better memory key from the conversation text."""
        try:
            # Extract the first user message to create a meaningful key
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('user:') or line.startswith('User:'):
                    # Clean up the user message for the key
                    content = line.replace('user:', '').replace('User:', '').strip()
                    if content and len(content) > 10:
                        # Take first 40 characters and clean up
                        key = content[:40].strip()
                        # Remove common words and clean up
                        key = key.replace('Hello!', '').replace('Hello', '').replace('Hi', '').replace('Hey', '').strip()
                        if key:
                            return f"memory_{len(self.memory_cache) + 1}_{key[:30]}"
            
            # Fallback key
            return f"memory_{len(self.memory_cache) + 1}_conversation"
            
        except Exception as e:
            self.logger.debug(f"Memory key generation failed: {e}")
            return f"memory_{len(self.memory_cache) + 1}_fallback"
