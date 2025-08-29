"""
Conversation Worker module for Mythic-Lite chatbot system.

Handles conversation logic and LLM interactions, keeping the orchestrator
focused on coordination rather than direct model access.
"""

import time
from typing import Optional, Dict, List, Generator, Any
from pathlib import Path

from ..core.llm import ChatMessage
from ..utils.logger import get_logger


class ConversationWorker:
    """Worker class for handling conversation logic and LLM interactions."""
    
    def __init__(self, config: Optional[Any] = None):
        if config is None:
            raise ValueError("Conversation worker requires a configuration object")
        
        self.config = config
        self.logger = get_logger("conversation-worker")
        
        # Worker references (set by orchestrator)
        self.llm_worker = None
        self.memory_worker = None
        
        # Conversation state
        self.conversation_history = []
        self.current_context = {}
        
        # Performance tracking
        self.total_conversations = 0
        self.average_response_time = 0.0
        
        self.logger.debug("ConversationWorker initialized")
    
    def set_workers(self, llm_worker, memory_worker):
        """Set worker references from the orchestrator."""
        self.llm_worker = llm_worker
        self.memory_worker = memory_worker
        self.logger.debug("Worker references set")
    
    def initialize(self) -> bool:
        """Initialize the conversation worker."""
        try:
            if not self.llm_worker or not self.llm_worker.is_available():
                self.logger.error("LLM worker not available")
                return False
            
            if not self.memory_worker:
                self.logger.warning("Memory worker not available - memory features will be disabled")
            
            self.logger.success("Conversation worker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize conversation worker: {e}")
            return False
    
    def process_user_input(self, user_input: str, use_audio: bool = False) -> str:
        """Process user input and generate a response."""
        if not self.llm_worker or not self.llm_worker.is_available():
            return "System not available. Please wait..."
        
        start_time = time.time()
        
        try:
            # Add user input to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Recall relevant memories if memory worker is available
            relevant_memories = []
            if self.memory_worker:
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
            if self.memory_worker:
                self.memory_worker.store_conversation_memory(user_input, response, context)
            
            # Update conversation count and performance metrics
            self.total_conversations += 1
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process user input: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def process_user_input_stream(self, user_input: str, use_audio: bool = False):
        """Process user input with streaming response."""
        if not self.llm_worker or not self.llm_worker.is_available():
            yield "System not available. Please wait..."
            return
        
        start_time = time.time()
        
        try:
            # Add user input to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Recall relevant memories if memory worker is available
            relevant_memories = []
            if self.memory_worker:
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
            if self.memory_worker:
                self.memory_worker.store_conversation_memory(user_input, accumulated_response, context)
            
            # Update conversation count and performance metrics
            self.total_conversations += 1
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time)
            
        except Exception as e:
            self.logger.error(f"Failed to process user input stream: {e}")
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_context(self, user_input: str, relevant_memories: List[Dict]) -> Dict[str, Any]:
        """Build context for the current conversation."""
        context = {
            'user_input': user_input,
            'timestamp': time.time(),
            'conversation_count': self.total_conversations,
            'relevant_memories': relevant_memories
        }
        
        # Add system context
        if hasattr(self.config, 'system'):
            context['system'] = {
                'character': getattr(self.config.system, 'character', 'Mythic'),
                'personality': getattr(self.config.system, 'personality', '19th century mercenary'),
                'context': getattr(self.config.system, 'context', '')
            }
        
        return context
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance tracking metrics."""
        if self.total_conversations == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_conversations - 1) + response_time) 
                / self.total_conversations
            )
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        self.current_context.clear()
        self.logger.info("Conversation history cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'total_conversations': self.total_conversations,
            'average_response_time': self.average_response_time,
            'conversation_history_length': len(self.conversation_history)
        }
    
    def get_status(self) -> str:
        """Get the status of the conversation worker."""
        if not self.llm_worker:
            return "Conversation: No LLM worker"
        
        if not self.llm_worker.is_available():
            return "Conversation: LLM not available"
        
        return f"Conversation: Active ({self.total_conversations} conversations)"
    
    def cleanup(self):
        """Cleanup conversation worker resources."""
        try:
            self.conversation_history.clear()
            self.current_context.clear()
            self.logger.info("Conversation worker cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during conversation worker cleanup: {e}")
    
    def is_available(self) -> bool:
        """Check if the conversation worker is available for use."""
        return self.llm_worker and self.llm_worker.is_available()