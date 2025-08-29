"""
Memory Worker module for Mythic-Lite chatbot system.

Handles conversation memory, summarization, and recall using the LLM abstraction layer.
"""

import threading
import time
from typing import Optional, Any, Dict, List
from pathlib import Path

from ..core.llm import ChatMessage
from ..utils.logger import get_logger


class MemoryWorker:
    """Worker class for handling conversation memory, summarization, and recall using the LLM abstraction layer."""
    
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
        
        # Memory storage
        self.memory_file = Path("memory") / "conversation_memory.json"
        self.memory_file.parent.mkdir(exist_ok=True)
        
        self.logger.debug("MemoryWorker initialized")
        
    def set_llm_worker(self, llm_worker):
        """Set the LLM worker reference for memory operations."""
        self.llm_worker = llm_worker
        self.is_enabled = llm_worker is not None and llm_worker.is_available()
        self.logger.debug(f"LLM worker reference set, memory enabled: {self.is_enabled}")
        
    def initialize(self) -> bool:
        """Initialize the memory worker."""
        try:
            if not self.llm_worker or not self.llm_worker.is_available():
                self.logger.warning("LLM worker not available, memory operations will be limited")
                self.is_initialized = False
                self.is_enabled = False
                return False
            
            self.is_initialized = True
            self.is_enabled = True
            self.initialization_error = None
            
            # Load existing memory
            self._load_memory()
            
            self.logger.success("Memory worker initialized successfully using LLM abstraction layer!")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.warning(f"Memory worker initialization failed: {e}")
            self.is_initialized = False
            self.is_enabled = False
            return False

    def create_memory_summary(self, text, max_length=100):
        """Create intelligent memory summaries using the LLM abstraction layer."""
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
            
            # Generate summary using the LLM abstraction layer
            result = [None]
            exception = [None]
            
            def generate_summary():
                try:
                    response = self.llm_worker.generate_chat_response(
                        messages=summary_messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    result[0] = response
                except Exception as e:
                    exception[0] = e
            
            # Start generation in separate thread with timeout
            summary_thread = threading.Thread(target=generate_summary)
            summary_thread.daemon = True
            summary_thread.start()
            
            # Wait for completion with timeout
            summary_thread.join(timeout=30)
            
            if exception[0]:
                self.logger.warning(f"Memory summary generation failed: {exception[0]}")
                return None
            
            if result[0]:
                summary = result[0].strip()
                if len(summary) > max_length:
                    summary = summary[:max_length-3] + "..."
                return summary
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create memory summary: {e}")
            return None

    def store_conversation_memory(self, user_input, ai_response, context=None):
        """Store conversation in memory with intelligent summarization."""
        if not self.is_enabled:
            return
        
        try:
            timestamp = time.time()
            
            # Create conversation entry
            conversation_entry = {
                'timestamp': timestamp,
                'user_input': user_input,
                'ai_response': ai_response,
                'context': context or {},
                'summary': None
            }
            
            # Generate summary if we have enough content
            combined_text = f"{user_input}\n{ai_response}"
            if len(combined_text) > 50:  # Only summarize longer conversations
                summary = self.create_memory_summary(combined_text)
                if summary:
                    conversation_entry['summary'] = summary
            
            # Store in memory cache
            memory_key = f"conv_{timestamp}"
            self.memory_cache[memory_key] = conversation_entry
            
            # Update conversation patterns
            self._update_conversation_patterns(user_input, ai_response)
            
            # Save to persistent storage
            self._save_memory()
            
            self.logger.debug(f"Stored conversation memory: {memory_key}")
            
        except Exception as e:
            self.logger.error(f"Failed to store conversation memory: {e}")

    def recall_relevant_memory(self, query, max_results=5):
        """Recall relevant memories based on a query."""
        if not self.is_enabled or not self.memory_cache:
            return []
        
        try:
            # Simple keyword-based recall for now
            # TODO: Implement semantic search using LLM embedding
            relevant_memories = []
            query_lower = query.lower()
            
            for memory_key, memory_data in self.memory_cache.items():
                relevance_score = 0
                
                # Check user input
                if memory_data.get('user_input'):
                    if query_lower in memory_data['user_input'].lower():
                        relevance_score += 2
                
                # Check AI response
                if memory_data.get('ai_response'):
                    if query_lower in memory_data['ai_response'].lower():
                        relevance_score += 1
                
                # Check summary
                if memory_data.get('summary'):
                    if query_lower in memory_data['summary'].lower():
                        relevance_score += 3
                
                if relevance_score > 0:
                    relevant_memories.append({
                        'key': memory_key,
                        'data': memory_data,
                        'relevance': relevance_score
                    })
            
            # Sort by relevance and return top results
            relevant_memories.sort(key=lambda x: x['relevance'], reverse=True)
            return relevant_memories[:max_results]
            
        except Exception as e:
            self.logger.error(f"Failed to recall relevant memory: {e}")
            return []

    def get_memory_stats(self):
        """Get statistics about stored memories."""
        try:
            total_memories = len(self.memory_cache)
            total_summaries = sum(1 for m in self.memory_cache.values() if m.get('summary'))
            
            # Calculate memory age
            if self.memory_cache:
                oldest_timestamp = min(m['timestamp'] for m in self.memory_cache.values())
                newest_timestamp = max(m['timestamp'] for m in self.memory_cache.values())
                memory_age_hours = (newest_timestamp - oldest_timestamp) / 3600
            else:
                memory_age_hours = 0
            
            return {
                'total_memories': total_memories,
                'total_summaries': total_summaries,
                'memory_age_hours': memory_age_hours,
                'is_enabled': self.is_enabled,
                'is_initialized': self.is_initialized
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {}

    def _update_conversation_patterns(self, user_input, ai_response):
        """Update conversation pattern tracking."""
        try:
            # Extract key phrases from user input
            user_words = user_input.lower().split()
            common_words = [w for w in user_words if len(w) > 3]
            
            for word in common_words:
                if word not in self.conversation_patterns:
                    self.conversation_patterns[word] = 0
                self.conversation_patterns[word] += 1
            
            # Track character-specific patterns
            if 'mythic' in ai_response.lower():
                self.character_memory['mythic_mentions'] = self.character_memory.get('mythic_mentions', 0) + 1
            
        except Exception as e:
            self.logger.debug(f"Failed to update conversation patterns: {e}")

    def _save_memory(self):
        """Save memory to persistent storage."""
        try:
            import json
            
            # Prepare data for serialization
            serializable_memory = {}
            for key, value in self.memory_cache.items():
                # Ensure all values are JSON serializable
                serializable_memory[key] = value
            
            with open(self.memory_file, 'w') as f:
                json.dump(serializable_memory, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")

    def _load_memory(self):
        """Load memory from persistent storage."""
        try:
            import json
            
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    self.memory_cache = json.load(f)
                self.logger.info(f"Loaded {len(self.memory_cache)} memories from storage")
            else:
                self.memory_cache = {}
                self.logger.info("No existing memory found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Failed to load memory: {e}")
            self.memory_cache = {}

    def cleanup(self):
        """Cleanup memory worker resources."""
        try:
            # Save memory before cleanup
            self._save_memory()
            
            self.is_initialized = False
            self.is_enabled = False
            self.initialization_error = None
            
            self.logger.info("Memory worker cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during memory worker cleanup: {e}")

    def get_status(self) -> str:
        """Get the status of the memory worker."""
        if self.is_initialized and self.is_enabled:
            memory_count = len(self.memory_cache)
            return f"Memory: Active ({memory_count} memories stored)"
        elif self.initialization_error:
            return f"Memory: Error - {self.initialization_error}"
        else:
            return "Memory: Not initialized"
