"""
Memory Worker module for Mythic-Lite chatbot system.

Handles conversation memory, summarization, and recall using the LLM abstraction layer,
providing intelligent memory management with persistent storage.
"""

import threading
import time
import json
from typing import Optional, Any, Dict, List
from pathlib import Path
from datetime import datetime, timedelta

from ..core.llm import ChatMessage
from ..utils.logger import get_logger, logged_operation


class MemoryWorker:
    """Worker class for handling conversation memory with intelligent summarization."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the memory worker with configuration."""
        if config is None:
            raise ValueError("Memory worker requires a configuration object")
        
        self.config = config
        self.logger = get_logger("memory-worker")
        
        # Memory management features
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.conversation_patterns: Dict[str, int] = {}
        self.character_memory: Dict[str, Any] = {}
        
        # LLM reference (will be set by the orchestrator)
        self.llm_worker = None
        
        # Memory storage
        self.memory_file = Path("memory") / "conversation_memory.json"
        self.memory_file.parent.mkdir(exist_ok=True)
        
        # Performance tracking
        self.total_memories_stored = 0
        self.total_memories_recalled = 0
        self.total_summaries_generated = 0
        
        # Worker state
        self.is_initialized = False
        self.is_enabled = False
        self.initialization_error: Optional[str] = None
        
        self.logger.debug("Memory worker initialized")
        
    def set_llm_worker(self, llm_worker):
        """Set the LLM worker reference for memory operations."""
        self.llm_worker = llm_worker
        self.is_enabled = llm_worker is not None and llm_worker.is_available()
        self.logger.debug(f"LLM worker reference set, memory enabled: {self.is_enabled}")
        
    def initialize(self) -> bool:
        """Initialize the memory worker."""
        with logged_operation(self.logger, "memory_worker_initialize"):
            try:
                if not self.llm_worker or not self.llm_worker.is_available():
                    self.logger.warning("LLM worker not available, memory operations will be limited")
                    self.is_initialized = False
                    self.is_enabled = False
                    return False
                
                # Load existing memory
                self._load_memory()
                
                # Clean up old memories
                self._cleanup_expired_memories()
                
                self.is_initialized = True
                self.is_enabled = True
                self.initialization_error = None
                
                self.logger.info(f"Memory worker initialized successfully with {len(self.memory_cache)} existing memories")
                return True
                
            except Exception as e:
                self.initialization_error = str(e)
                self.logger.error(f"Memory worker initialization failed: {e}")
                self.is_initialized = False
                self.is_enabled = False
                return False

    def create_memory_summary(self, text: str, max_length: int = 100) -> Optional[str]:
        """Create intelligent memory summaries using the LLM abstraction layer."""
        if not self.is_enabled or not self.llm_worker or not text:
            return None
        
        with logged_operation(self.logger, "create_memory_summary", text_length=len(text)):
            try:
                # Use configuration settings for memory generation
                max_tokens = getattr(self.config.memory, 'max_tokens', 120)
                temperature = getattr(self.config.memory, 'temperature', 0.1)
                
                # Create a better prompt for memory summarization
                summary_messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Summarize this conversation in a clear, concise way, focusing on what was discussed and any important points."
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
                    
                    self.total_summaries_generated += 1
                    return summary
                
                return None
                
            except Exception as e:
                self.logger.error(f"Failed to create memory summary: {e}")
                return None

    def store_conversation_memory(self, user_input: str, ai_response: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Store conversation in memory with intelligent summarization."""
        if not self.is_enabled:
            return
        
        with logged_operation(self.logger, "store_conversation_memory"):
            try:
                timestamp = time.time()
                
                # Create conversation entry
                conversation_entry = {
                    'timestamp': timestamp,
                    'user_input': user_input,
                    'ai_response': ai_response,
                    'context': context or {},
                    'summary': None,
                    'keywords': self._extract_keywords(user_input + " " + ai_response)
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
                
                self.total_memories_stored += 1
                self.logger.debug(f"Stored conversation memory: {memory_key}")
                
            except Exception as e:
                self.logger.error(f"Failed to store conversation memory: {e}")

    def recall_relevant_memory(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Recall relevant memories based on a query with relevance scoring."""
        if not self.is_enabled or not self.memory_cache:
            return []
        
        with logged_operation(self.logger, "recall_relevant_memory", query_length=len(query)):
            try:
                # Simple keyword-based recall for now
                # TODO: Implement semantic search using LLM embedding
                relevant_memories = []
                query_lower = query.lower()
                query_words = set(query_lower.split())
                
                for memory_key, memory_data in self.memory_cache.items():
                    relevance_score = 0
                    
                    # Check user input
                    if memory_data.get('user_input'):
                        user_input_lower = memory_data['user_input'].lower()
                        if query_lower in user_input_lower:
                            relevance_score += 2
                        
                        # Check for word overlap
                        user_words = set(user_input_lower.split())
                        word_overlap = len(query_words.intersection(user_words))
                        relevance_score += word_overlap * 0.5
                    
                    # Check AI response
                    if memory_data.get('ai_response'):
                        ai_response_lower = memory_data['ai_response'].lower()
                        if query_lower in ai_response_lower:
                            relevance_score += 1
                    
                    # Check summary
                    if memory_data.get('summary'):
                        summary_lower = memory_data['summary'].lower()
                        if query_lower in summary_lower:
                            relevance_score += 3
                    
                    # Check keywords
                    if memory_data.get('keywords'):
                        keyword_overlap = len(query_words.intersection(memory_data['keywords']))
                        relevance_score += keyword_overlap * 0.3
                    
                    if relevance_score > 0:
                        relevant_memories.append({
                            'key': memory_key,
                            'data': memory_data,
                            'relevance': relevance_score
                        })
                
                # Sort by relevance and return top results
                relevant_memories.sort(key=lambda x: x['relevance'], reverse=True)
                
                self.total_memories_recalled += len(relevant_memories[:max_results])
                return relevant_memories[:max_results]
                
            except Exception as e:
                self.logger.error(f"Failed to recall relevant memory: {e}")
                return []

    def get_memory_stats(self) -> Dict[str, Any]:
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
                'total_memories_stored': self.total_memories_stored,
                'total_memories_recalled': self.total_memories_recalled,
                'total_summaries_generated': self.total_summaries_generated,
                'is_enabled': self.is_enabled,
                'is_initialized': self.is_initialized,
                'cache_size': len(self.memory_cache),
                'patterns_tracked': len(self.conversation_patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {}

    def _update_conversation_patterns(self, user_input: str, ai_response: str) -> None:
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

    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text for better memory recall."""
        try:
            # Simple keyword extraction
            words = text.lower().split()
            # Filter out common words and short words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = {word for word in words if len(word) > 3 and word not in stop_words}
            return keywords
        except Exception as e:
            self.logger.debug(f"Failed to extract keywords: {e}")
            return set()

    def _cleanup_expired_memories(self) -> None:
        """Clean up memories that have expired based on TTL."""
        try:
            if not self.memory_cache:
                return
            
            ttl_hours = getattr(self.config.memory, 'memory_ttl_hours', 24 * 7)
            cutoff_time = time.time() - (ttl_hours * 3600)
            
            expired_keys = [
                key for key, memory in self.memory_cache.items()
                if memory.get('timestamp', 0) < cutoff_time
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            if expired_keys:
                self.logger.info(f"Cleaned up {len(expired_keys)} expired memories")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")

    def _save_memory(self) -> None:
        """Save memory to persistent storage."""
        try:
            # Prepare data for serialization
            serializable_memory = {}
            for key, value in self.memory_cache.items():
                # Ensure all values are JSON serializable
                serializable_memory[key] = value
            
            with open(self.memory_file, 'w') as f:
                json.dump(serializable_memory, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")

    def _load_memory(self) -> None:
        """Load memory from persistent storage."""
        try:
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

    def clear_memory(self) -> None:
        """Clear all stored memories."""
        with logged_operation(self.logger, "clear_memory"):
            try:
                self.memory_cache.clear()
                self.conversation_patterns.clear()
                self.character_memory.clear()
                
                # Remove memory file
                if self.memory_file.exists():
                    self.memory_file.unlink()
                
                self.logger.info("All memories cleared")
                
            except Exception as e:
                self.logger.error(f"Failed to clear memory: {e}")

    def export_memory(self, file_path: str) -> bool:
        """Export memory to a file."""
        try:
            export_data = {
                'memories': self.memory_cache,
                'patterns': self.conversation_patterns,
                'character_memory': self.character_memory,
                'export_timestamp': time.time(),
                'stats': self.get_memory_stats()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Memory exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export memory: {e}")
            return False

    def import_memory(self, file_path: str) -> bool:
        """Import memory from a file."""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            if 'memories' in import_data:
                self.memory_cache.update(import_data['memories'])
            
            if 'patterns' in import_data:
                self.conversation_patterns.update(import_data['patterns'])
            
            if 'character_memory' in import_data:
                self.character_memory.update(import_data['character_memory'])
            
            self._save_memory()
            self.logger.info(f"Memory imported from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import memory: {e}")
            return False

    def cleanup(self):
        """Cleanup memory worker resources."""
        with logged_operation(self.logger, "memory_worker_cleanup"):
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

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the memory worker."""
        health = {
            'status': 'healthy' if self.is_enabled else 'unhealthy',
            'initialized': self.is_initialized,
            'enabled': self.is_enabled,
            'llm_available': self.llm_worker is not None and self.llm_worker.is_available(),
            'memory_count': len(self.memory_cache),
            'error': self.initialization_error
        }
        
        # Test memory operations if available
        if self.is_enabled:
            try:
                test_memories = self.recall_relevant_memory("test", max_results=1)
                health['test_recall'] = len(test_memories) >= 0
            except Exception as e:
                health['test_recall'] = False
                health['test_error'] = str(e)
        
        return health
