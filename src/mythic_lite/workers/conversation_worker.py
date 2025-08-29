"""
Conversation Worker module for Mythic-Lite chatbot system.

Handles conversation logic and LLM interactions, keeping the orchestrator
focused on coordination rather than direct model access.
"""

import time
from typing import Optional, Dict, List, Generator, Any
from pathlib import Path

from ..core.llm import ChatMessage
from ..utils.logger import get_logger, logged_operation


class ConversationWorker:
    """Worker class for handling conversation logic and LLM interactions."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the conversation worker with configuration."""
        if config is None:
            raise ValueError("Conversation worker requires a configuration object")
        
        self.config = config
        self.logger = get_logger("conversation-worker")
        
        # Worker references (set by orchestrator)
        self.llm_worker = None
        self.memory_worker = None
        
        # Conversation state
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        
        # Performance tracking
        self.total_conversations = 0
        self.average_response_time = 0.0
        self.total_response_time = 0.0
        
        # Worker state
        self.is_initialized = False
        self.initialization_error: Optional[str] = None
        
        self.logger.debug("Conversation worker initialized")
    
    def set_workers(self, llm_worker, memory_worker):
        """Set worker references from the orchestrator."""
        self.llm_worker = llm_worker
        self.memory_worker = memory_worker
        self.logger.debug("Worker references set")
    
    def initialize(self) -> bool:
        """Initialize the conversation worker."""
        with logged_operation(self.logger, "conversation_worker_initialize"):
            try:
                if not self.llm_worker or not self.llm_worker.is_available():
                    self.logger.error("LLM worker not available")
                    return False
                
                if not self.memory_worker:
                    self.logger.warning("Memory worker not available - memory features will be disabled")
                
                self.is_initialized = True
                self.initialization_error = None
                
                self.logger.info("Conversation worker initialized successfully")
                return True
                
            except Exception as e:
                self.initialization_error = str(e)
                self.logger.error(f"Failed to initialize conversation worker: {e}")
                return False
    
    def process_user_input(self, user_input: str, use_audio: bool = False) -> str:
        """Process user input and generate a response."""
        if not self.llm_worker or not self.llm_worker.is_available():
            return "System not available. Please wait..."
        
        start_time = time.time()
        
        with logged_operation(self.logger, "process_user_input", input_length=len(user_input)):
            try:
                # Add user input to conversation history
                self.conversation_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': time.time()
                })
                
                # Recall relevant memories if memory worker is available
                relevant_memories = []
                if self.memory_worker and self.memory_worker.is_enabled:
                    relevant_memories = self.memory_worker.recall_relevant_memory(user_input)
                
                # Build context with memories
                context = self._build_context(user_input, relevant_memories)
                
                # Generate response using LLM worker
                response = self.llm_worker.generate_chat_response(
                    messages=self.conversation_history,
                    max_tokens=self.config.llm.max_tokens,
                    temperature=self.config.llm.temperature
                )
                
                if not response:
                    response = "I apologize, but I'm having trouble generating a response right now."
                
                # Add AI response to conversation history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': time.time()
                })
                
                # Store in memory if available
                if self.memory_worker and self.memory_worker.is_enabled:
                    self.memory_worker.store_conversation_memory(user_input, response, context)
                
                # Update conversation count and performance metrics
                self.total_conversations += 1
                response_time = time.time() - start_time
                self._update_performance_metrics(response_time)
                
                return response
                
            except Exception as e:
                self.logger.error(f"Failed to process user input: {e}")
                return f"I apologize, but I encountered an error: {str(e)}"
    
    def process_user_input_stream(self, user_input: str, use_audio: bool = False) -> Generator[str, None, None]:
        """Process user input with streaming response."""
        if not self.llm_worker or not self.llm_worker.is_available():
            yield "System not available. Please wait..."
            return
        
        start_time = time.time()
        
        with logged_operation(self.logger, "process_user_input_stream", input_length=len(user_input)):
            try:
                # Add user input to conversation history
                self.conversation_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': time.time()
                })
                
                # Recall relevant memories if memory worker is available
                relevant_memories = []
                if self.memory_worker and self.memory_worker.is_enabled:
                    relevant_memories = self.memory_worker.recall_relevant_memory(user_input)
                
                # Build context with memories
                context = self._build_context(user_input, relevant_memories)
                
                # Generate streaming response using LLM worker
                accumulated_response = ""
                
                for token, full_response in self.llm_worker.generate_chat_response_stream(
                    messages=self.conversation_history,
                    max_tokens=self.config.llm.max_tokens,
                    temperature=self.config.llm.temperature
                ):
                    accumulated_response = full_response
                    yield token
                
                # Add AI response to conversation history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': accumulated_response,
                    'timestamp': time.time()
                })
                
                # Store in memory if available
                if self.memory_worker and self.memory_worker.is_enabled:
                    self.memory_worker.store_conversation_memory(user_input, accumulated_response, context)
                
                # Update conversation count and performance metrics
                self.total_conversations += 1
                response_time = time.time() - start_time
                self._update_performance_metrics(response_time)
                
            except Exception as e:
                self.logger.error(f"Failed to process user input stream: {e}")
                yield f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_context(self, user_input: str, relevant_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build context for the current conversation."""
        context = {
            'user_input': user_input,
            'timestamp': time.time(),
            'conversation_count': self.total_conversations,
            'relevant_memories': relevant_memories,
            'conversation_history_length': len(self.conversation_history)
        }
        
        # Add system context
        if hasattr(self.config, 'system'):
            context['system'] = {
                'character': getattr(self.config.system, 'character', 'Mythic'),
                'personality': getattr(self.config.system, 'personality', '19th century mercenary'),
                'context': getattr(self.config.system, 'context', '')
            }
        
        # Add conversation configuration
        if hasattr(self.config, 'conversation'):
            context['conversation'] = {
                'system_prompt': getattr(self.config.conversation, 'system_prompt', ''),
                'max_history_length': getattr(self.config.conversation, 'max_history_length', 50),
                'enable_streaming': getattr(self.config.conversation, 'enable_streaming', True)
            }
        
        return context
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance tracking metrics."""
        self.total_response_time += response_time
        
        # Calculate running average
        self.average_response_time = self.total_response_time / self.total_conversations
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return {'error': 'No conversation history'}
        
        try:
            user_messages = [msg for msg in self.conversation_history if msg['role'] == 'user']
            assistant_messages = [msg for msg in self.conversation_history if msg['role'] == 'assistant']
            
            return {
                'total_messages': len(self.conversation_history),
                'user_messages': len(user_messages),
                'assistant_messages': len(assistant_messages),
                'conversation_duration': (
                    self.conversation_history[-1]['timestamp'] - self.conversation_history[0]['timestamp']
                    if len(self.conversation_history) > 1 else 0
                ),
                'last_user_input': user_messages[-1]['content'] if user_messages else None,
                'last_assistant_response': assistant_messages[-1]['content'] if assistant_messages else None
            }
        except Exception as e:
            return {'error': f'Failed to generate summary: {e}'}
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        with logged_operation(self.logger, "clear_conversation_history"):
            try:
                self.conversation_history.clear()
                self.current_context.clear()
                self.logger.info("Conversation history cleared")
            except Exception as e:
                self.logger.error(f"Failed to clear conversation history: {e}")
    
    def add_system_message(self, content: str):
        """Add a system message to the conversation history."""
        try:
            system_message = {
                'role': 'system',
                'content': content,
                'timestamp': time.time()
            }
            
            # Insert at the beginning to maintain conversation flow
            self.conversation_history.insert(0, system_message)
            
            self.logger.debug(f"Added system message: {content[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Failed to add system message: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'total_conversations': self.total_conversations,
            'average_response_time': self.average_response_time,
            'total_response_time': self.total_response_time,
            'conversation_history_length': len(self.conversation_history),
            'conversations_per_minute': (
                self.total_conversations / (self.total_response_time / 60)
                if self.total_response_time > 0 else 0
            )
        }
    
    def get_status(self) -> str:
        """Get the status of the conversation worker."""
        if not self.llm_worker:
            return "Conversation: No LLM worker"
        
        if not self.llm_worker.is_available():
            return "Conversation: LLM not available"
        
        return f"Conversation: Active ({self.total_conversations} conversations)"
    
    def reset_performance_metrics(self):
        """Reset performance tracking metrics."""
        self.total_conversations = 0
        self.average_response_time = 0.0
        self.total_response_time = 0.0
        
        self.logger.info("Performance metrics reset")
    
    def cleanup(self):
        """Cleanup conversation worker resources."""
        with logged_operation(self.logger, "conversation_worker_cleanup"):
            try:
                self.conversation_history.clear()
                self.current_context.clear()
                self.is_initialized = False
                self.initialization_error = None
                
                self.logger.info("Conversation worker cleaned up")
                
            except Exception as e:
                self.logger.error(f"Error during conversation worker cleanup: {e}")
    
    def is_available(self) -> bool:
        """Check if the conversation worker is available for use."""
        return self.is_initialized and self.llm_worker and self.llm_worker.is_available()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the conversation worker."""
        health = {
            'status': 'healthy' if self.is_available() else 'unhealthy',
            'initialized': self.is_initialized,
            'llm_available': self.llm_worker is not None and self.llm_worker.is_available(),
            'memory_available': self.memory_worker is not None and self.memory_worker.is_enabled,
            'total_conversations': self.total_conversations,
            'conversation_history_length': len(self.conversation_history),
            'error': self.initialization_error
        }
        
        # Test conversation processing if available
        if self.is_available():
            try:
                test_response = self.process_user_input("test", use_audio=False)
                health['test_response'] = bool(test_response)
            except Exception as e:
                health['test_response'] = False
                health['test_error'] = str(e)
        
        return health
    
    def export_conversation(self, file_path: str) -> bool:
        """Export conversation history to a file."""
        try:
            import json
            
            export_data = {
                'conversation_history': self.conversation_history,
                'performance_stats': self.get_performance_stats(),
                'conversation_summary': self.get_conversation_summary(),
                'export_timestamp': time.time()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Conversation exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export conversation: {e}")
            return False