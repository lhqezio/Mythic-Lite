"""
Main orchestrator module for Mythic-Lite chatbot system.

Coordinates all workers and manages the main chatbot interface using the LLM abstraction layer.
"""

import time
import json
import os
from datetime import datetime
from typing import Optional, Any, Dict, List

from .config import get_config
from ..utils.logger import get_logger
from ..utils.windows_input import safe_input, safe_choice
from ..workers import ASRWorker, LLMWorker, MemoryWorker, TTSWorker


class ChatbotOrchestrator:
    """Main orchestrator class that coordinates all workers."""
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config or get_config()
        self.logger = get_logger("orchestrator")
        
        # Create worker instances but don't initialize them yet
        self.llm_worker = LLMWorker(self.config)
        self.memory_worker = MemoryWorker(self.config)
        self.tts_worker = TTSWorker(self.config)
        self.asr_worker = ASRWorker(self.config)
        
        # Set LLM worker reference in memory worker
        self.memory_worker.set_llm_worker(self.llm_worker)
        
        # Debug mode from configuration
        self.debug_mode = self.config.debug_mode
        
        # Performance tracking
        self.start_time = time.time()
        self.total_conversations = 0
        self.benchmark_results = None  # Store benchmark test results
        
        # Track initialization status
        self._initialized = False
        
        # Conversation state
        self.conversation_history = []
        self.current_context = {}
        
        self.logger.info("ChatbotOrchestrator created (not yet initialized)")
    
    def initialize_workers(self) -> bool:
        """Initialize all worker components."""
        if self._initialized:
            self.logger.info("Workers already initialized, skipping...")
            return True
        
        self.logger.info("Initializing Mythic's systems...")
        
        try:
            # Initialize LLM worker
            self.logger.debug("Initializing LLM worker...")
            if not self.llm_worker.initialize():
                self.logger.critical("Failed to initialize LLM worker!")
                return False
            self.logger.debug("LLM worker initialized successfully")
            
            # Update memory worker with LLM reference
            self.memory_worker.set_llm_worker(self.llm_worker)
            
            # Initialize memory worker
            self.logger.debug("Initializing memory worker...")
            if not self.memory_worker.initialize():
                self.logger.warning("Memory worker initialization failed - memory management will be limited")
            else:
                self.logger.debug("Memory worker initialized successfully")
            
            # Initialize TTS worker
            self.logger.debug("Initializing TTS worker...")
            if not self.tts_worker.initialize():
                self.logger.warning("TTS initialization failed - audio will be disabled")
            else:
                self.logger.success("TTS system initialized successfully!")
                self.logger.debug("TTS worker initialized successfully")
            
            # Initialize ASR worker if enabled
            if self.config.asr.enable_asr:
                try:
                    self.logger.debug("Initializing ASR worker...")
                    self.asr_worker.set_callbacks(
                        on_transcription=self._handle_speech_input,
                        on_partial=self._handle_partial_speech
                    )
                    if not self.asr_worker.initialize():
                        self.logger.warning("ASR initialization failed - voice input will be disabled")
                    else:
                        self.logger.success("ASR system initialized successfully!")
                        self.logger.debug("ASR worker initialized successfully")
                except Exception as e:
                    self.logger.warning(f"ASR initialization failed: {e}")
            else:
                self.logger.info("ASR disabled in configuration")
            
            # Mark as initialized
            self._initialized = True
            self.logger.success("All workers initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workers: {e}")
            return False
    
    def process_user_input(self, user_input: str, use_audio: bool = False) -> str:
        """Process user input and generate a response."""
        if not self._initialized:
            return "System not initialized. Please wait..."
        
        try:
            # Add user input to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Recall relevant memories
            relevant_memories = self.memory_worker.recall_relevant_memory(user_input)
            
            # Build context with memories
            context = self._build_context(user_input, relevant_memories)
            
            # Generate response using LLM abstraction layer
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
            
            # Store in memory
            self.memory_worker.store_conversation_memory(user_input, response, context)
            
            # Update conversation count
            self.total_conversations += 1
            
            # Generate audio if requested
            if use_audio and self.tts_worker.is_available():
                try:
                    self.tts_worker.synthesize_speech(response)
                except Exception as e:
                    self.logger.warning(f"TTS failed: {e}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process user input: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def process_user_input_stream(self, user_input: str, use_audio: bool = False):
        """Process user input with streaming response."""
        if not self._initialized:
            yield "System not initialized. Please wait..."
            return
        
        try:
            # Add user input to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Recall relevant memories
            relevant_memories = self.memory_worker.recall_relevant_memory(user_input)
            
            # Build context with memories
            context = self._build_context(user_input, relevant_memories)
            
            # Generate streaming response using LLM abstraction layer
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
            
            # Store in memory
            self.memory_worker.store_conversation_memory(user_input, accumulated_response, context)
            
            # Update conversation count
            self.total_conversations += 1
            
            # Generate audio if requested
            if use_audio and self.tts_worker.is_available():
                try:
                    self.tts_worker.synthesize_speech(accumulated_response)
                except Exception as e:
                    self.logger.warning(f"TTS failed: {e}")
            
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
    
    def _handle_speech_input(self, transcription: str):
        """Handle speech input from ASR."""
        self.logger.info(f"Speech input: {transcription}")
        # Process speech input (could be implemented based on your needs)
    
    def _handle_partial_speech(self, partial: str):
        """Handle partial speech input from ASR."""
        self.logger.debug(f"Partial speech: {partial}")
        # Handle partial speech (could be implemented based on your needs)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of all system components."""
        return {
            'initialized': self._initialized,
            'llm_worker': self.llm_worker.get_status(),
            'memory_worker': self.memory_worker.get_status(),
            'tts_worker': self.tts_worker.get_status(),
            'asr_worker': self.asr_worker.get_status(),
            'total_conversations': self.total_conversations,
            'uptime_hours': (time.time() - self.start_time) / 3600,
            'conversation_history_length': len(self.conversation_history)
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'total_conversations': self.total_conversations,
            'uptime_hours': (time.time() - self.start_time) / 3600,
            'conversations_per_hour': (
                self.total_conversations / ((time.time() - self.start_time) / 3600)
                if (time.time() - self.start_time) > 0 else 0
            )
        }
        
        # Add worker-specific stats
        if self.llm_worker:
            stats['llm_stats'] = self.llm_worker.get_performance_stats()
        
        if self.memory_worker:
            stats['memory_stats'] = self.memory_worker.get_memory_stats()
        
        return stats
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run a benchmark test of the system."""
        if not self._initialized:
            return {'error': 'System not initialized'}
        
        self.logger.info("Running system benchmark...")
        start_time = time.time()
        
        try:
            # Test basic response generation
            test_input = "Hello, how are you today?"
            response = self.process_user_input(test_input)
            
            benchmark_time = time.time() - start_time
            
            self.benchmark_results = {
                'test_input': test_input,
                'response': response,
                'response_time': benchmark_time,
                'success': bool(response and len(response) > 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.success(f"Benchmark completed in {benchmark_time:.2f}s")
            return self.benchmark_results
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup all resources."""
        self.logger.info("Cleaning up orchestrator resources...")
        
        try:
            if self.llm_worker:
                self.llm_worker.cleanup()
            
            if self.memory_worker:
                self.memory_worker.cleanup()
            
            if self.tts_worker:
                self.tts_worker.cleanup()
            
            if self.asr_worker:
                self.asr_worker.cleanup()
            
            self._initialized = False
            self.logger.success("Orchestrator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def is_available(self) -> bool:
        """Check if the orchestrator is available for use."""
        return self._initialized and self.llm_worker.is_available() 
