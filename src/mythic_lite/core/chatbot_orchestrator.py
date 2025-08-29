"""
Main orchestrator module for Mythic-Lite chatbot system.

Coordinates all workers and manages the main chatbot interface.
The orchestrator should only coordinate workers, not directly interact with LLMs.
"""

import time
import json
import os
from datetime import datetime
from typing import Optional, Any, Dict, List, Generator
from pathlib import Path

from .config import get_config
from ..utils.logger import get_logger, logged_operation
from ..utils.windows_input import safe_input, safe_choice
from ..workers import ASRWorker, LLMWorker, MemoryWorker, TTSWorker, ConversationWorker


class ChatbotOrchestrator:
    """Main orchestrator class that coordinates all workers with performance monitoring."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the chatbot orchestrator with configuration."""
        self.config = config or get_config()
        self.logger = get_logger("orchestrator")
        
        # Create worker instances but don't initialize them yet
        self.llm_worker = LLMWorker(self.config)
        self.memory_worker = MemoryWorker(self.config)
        self.tts_worker = TTSWorker(self.config)
        self.asr_worker = ASRWorker(self.config)
        self.conversation_worker = ConversationWorker(self.config)
        
        # Set worker references
        self.memory_worker.set_llm_worker(self.llm_worker)
        self.conversation_worker.set_workers(self.llm_worker, self.memory_worker)
        
        # Debug mode from configuration
        self.debug_mode = self.config.system.debug_mode
        
        # Performance tracking
        self.start_time = time.time()
        self.total_conversations = 0
        self.benchmark_results: Optional[Dict[str, Any]] = None
        
        # Track initialization status
        self._initialized = False
        self.initialization_error: Optional[str] = None
        
        self.logger.info("Chatbot orchestrator created (not yet initialized)")
    
    def initialize_workers(self) -> bool:
        """Initialize all worker components."""
        if self._initialized:
            self.logger.info("Workers already initialized, skipping...")
            return True
        
        with logged_operation(self.logger, "orchestrator_initialize_workers"):
            try:
                self.logger.info("Initializing Mythic's systems...")
                
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
                
                # Initialize conversation worker
                self.logger.debug("Initializing conversation worker...")
                if not self.conversation_worker.initialize():
                    self.logger.critical("Failed to initialize conversation worker!")
                    return False
                self.logger.debug("Conversation worker initialized successfully")
                
                # Initialize TTS worker
                self.logger.debug("Initializing TTS worker...")
                if not self.tts_worker.initialize():
                    self.logger.warning("TTS initialization failed - audio will be disabled")
                else:
                    self.logger.info("TTS system initialized successfully!")
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
                            self.logger.info("ASR system initialized successfully!")
                            self.logger.debug("ASR worker initialized successfully")
                    except Exception as e:
                        self.logger.warning(f"ASR initialization failed: {e}")
                else:
                    self.logger.info("ASR disabled in configuration")
                
                # Mark as initialized
                self._initialized = True
                self.initialization_error = None
                self.logger.info("All workers initialized successfully!")
                return True
                
            except Exception as e:
                self.initialization_error = str(e)
                self.logger.error(f"Failed to initialize workers: {e}")
                return False
    
    def process_user_input(self, user_input: str, use_audio: bool = False) -> str:
        """Process user input and generate a response through the conversation worker."""
        if not self._initialized:
            return "System not initialized. Please wait..."
        
        with logged_operation(self.logger, "process_user_input", input_length=len(user_input)):
            try:
                # Delegate to conversation worker
                response = self.conversation_worker.process_user_input(user_input, use_audio)
                
                # Update conversation count
                self.total_conversations = self.conversation_worker.total_conversations
                
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
    
    def process_user_input_stream(self, user_input: str, use_audio: bool = False) -> Generator[str, None, None]:
        """Process user input with streaming response through the conversation worker."""
        if not self._initialized:
            yield "System not initialized. Please wait..."
            return
        
        with logged_operation(self.logger, "process_user_input_stream", input_length=len(user_input)):
            try:
                # Delegate to conversation worker
                accumulated_response = ""
                
                for token in self.conversation_worker.process_user_input_stream(user_input, use_audio):
                    accumulated_response += token
                    yield token
                
                # Update conversation count
                self.total_conversations = self.conversation_worker.total_conversations
                
                # Generate audio if requested
                if use_audio and self.tts_worker.is_available():
                    try:
                        self.tts_worker.synthesize_speech(accumulated_response)
                    except Exception as e:
                        self.logger.warning(f"TTS failed: {e}")
                
            except Exception as e:
                self.logger.error(f"Failed to process user input stream: {e}")
                yield f"I apologize, but I encountered an error: {str(e)}"
    
    def _handle_speech_input(self, transcription: str):
        """Handle speech input from ASR."""
        self.logger.info(f"Speech input: {transcription}")
        # Process speech input through conversation worker
        response = self.process_user_input(transcription, use_audio=True)
        self.logger.info(f"Response to speech: {response}")
    
    def _handle_partial_speech(self, partial: str):
        """Handle partial speech input from ASR."""
        self.logger.debug(f"Partial speech: {partial}")
        # Handle partial speech (could be implemented based on your needs)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of all system components."""
        return {
            'initialized': self._initialized,
            'error': self.initialization_error,
            'llm_worker': self.llm_worker.get_status(),
            'memory_worker': self.memory_worker.get_status(),
            'conversation_worker': self.conversation_worker.get_status(),
            'tts_worker': self.tts_worker.get_status(),
            'asr_worker': self.asr_worker.get_status(),
            'total_conversations': self.total_conversations,
            'uptime_hours': (time.time() - self.start_time) / 3600,
            'conversation_history_length': len(self.conversation_worker.get_conversation_history())
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'total_conversations': self.total_conversations,
            'uptime_hours': (time.time() - self.start_time) / 3600,
            'conversations_per_hour': (
                self.total_conversations / ((time.time() - self.start_time) / 3600)
                if (time.time() - self.start_time) > 0 else 0
            ),
            'system_health': self.get_system_health()
        }
        
        # Add worker-specific stats
        if self.llm_worker:
            stats['llm_stats'] = self.llm_worker.get_performance_stats()
        
        if self.memory_worker:
            stats['memory_stats'] = self.memory_worker.get_memory_stats()
        
        if self.conversation_worker:
            stats['conversation_stats'] = self.conversation_worker.get_performance_stats()
        
        return stats
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        health = {
            'overall_status': 'healthy' if self._initialized else 'unhealthy',
            'initialized': self._initialized,
            'error': self.initialization_error,
            'workers': {}
        }
        
        # Check each worker's health
        if self.llm_worker:
            health['workers']['llm'] = self.llm_worker.health_check()
        
        if self.memory_worker:
            health['workers']['memory'] = self.memory_worker.health_check()
        
        if self.conversation_worker:
            health['workers']['conversation'] = self.conversation_worker.health_check()
        
        if self.tts_worker:
            health['workers']['tts'] = {
                'status': 'healthy' if self.tts_worker.is_available() else 'unhealthy',
                'available': self.tts_worker.is_available()
            }
        
        if self.asr_worker:
            health['workers']['asr'] = {
                'status': 'healthy' if self.asr_worker.is_available() else 'unhealthy',
                'available': self.asr_worker.is_available()
            }
        
        return health
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run a benchmark test of the system."""
        if not self._initialized:
            return {'error': 'System not initialized'}
        
        with logged_operation(self.logger, "run_benchmark"):
            try:
                self.logger.info("Running system benchmark...")
                start_time = time.time()
                
                # Test basic response generation through conversation worker
                test_input = "Hello, how are you today?"
                response = self.process_user_input(test_input)
                
                benchmark_time = time.time() - start_time
                
                self.benchmark_results = {
                    'test_input': test_input,
                    'response': response,
                    'response_time': benchmark_time,
                    'success': bool(response and len(response) > 0),
                    'timestamp': datetime.now().isoformat(),
                    'system_stats': self.get_performance_stats()
                }
                
                self.logger.info(f"Benchmark completed in {benchmark_time:.2f}s")
                return self.benchmark_results
                
            except Exception as e:
                self.logger.error(f"Benchmark failed: {e}")
                return {'error': str(e)}
    
    def export_system_state(self, file_path: str) -> bool:
        """Export the current system state to a file."""
        try:
            export_data = {
                'system_status': self.get_system_status(),
                'performance_stats': self.get_performance_stats(),
                'system_health': self.get_system_health(),
                'conversation_history': self.conversation_worker.get_conversation_history(),
                'conversation_summary': self.conversation_worker.get_conversation_summary(),
                'export_timestamp': time.time(),
                'config': self.config.to_dict()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"System state exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export system state: {e}")
            return False
    
    def reset_system(self) -> bool:
        """Reset the system to initial state."""
        with logged_operation(self.logger, "reset_system"):
            try:
                # Reset performance metrics
                self.total_conversations = 0
                self.benchmark_results = None
                
                # Reset workers
                if self.conversation_worker:
                    self.conversation_worker.reset_performance_metrics()
                    self.conversation_worker.clear_conversation_history()
                
                if self.llm_worker:
                    self.llm_worker.reset_performance_metrics()
                
                if self.memory_worker:
                    self.memory_worker.clear_memory()
                
                self.logger.info("System reset completed")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to reset system: {e}")
                return False
    
    def cleanup(self):
        """Cleanup all resources."""
        with logged_operation(self.logger, "orchestrator_cleanup"):
            try:
                if self.llm_worker:
                    self.llm_worker.cleanup()
                
                if self.memory_worker:
                    self.memory_worker.cleanup()
                
                if self.conversation_worker:
                    self.conversation_worker.cleanup()
                
                if self.tts_worker:
                    self.tts_worker.cleanup()
                
                if self.asr_worker:
                    self.asr_worker.cleanup()
                
                self._initialized = False
                self.initialization_error = None
                
                self.logger.info("Orchestrator cleanup completed")
                
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
    
    def is_available(self) -> bool:
        """Check if the orchestrator is available for use."""
        return self._initialized and self.conversation_worker.is_available()
    
    def get_worker_status(self, worker_name: str) -> Dict[str, Any]:
        """Get status of a specific worker."""
        workers = {
            'llm': self.llm_worker,
            'memory': self.memory_worker,
            'conversation': self.conversation_worker,
            'tts': self.tts_worker,
            'asr': self.asr_worker
        }
        
        worker = workers.get(worker_name)
        if not worker:
            return {'error': f'Unknown worker: {worker_name}'}
        
        return {
            'name': worker_name,
            'available': worker.is_available() if hasattr(worker, 'is_available') else False,
            'status': worker.get_status() if hasattr(worker, 'get_status') else 'Unknown',
            'performance_stats': worker.get_performance_stats() if hasattr(worker, 'get_performance_stats') else {}
        }
    
    def restart_worker(self, worker_name: str) -> bool:
        """Restart a specific worker."""
        with logged_operation(self.logger, "restart_worker", worker_name=worker_name):
            try:
                workers = {
                    'llm': self.llm_worker,
                    'memory': self.memory_worker,
                    'conversation': self.conversation_worker,
                    'tts': self.tts_worker,
                    'asr': self.asr_worker
                }
                
                worker = workers.get(worker_name)
                if not worker:
                    self.logger.error(f"Unknown worker: {worker_name}")
                    return False
                
                # Cleanup and reinitialize worker
                if hasattr(worker, 'cleanup'):
                    worker.cleanup()
                
                if hasattr(worker, 'initialize'):
                    success = worker.initialize()
                    if success:
                        self.logger.info(f"Worker {worker_name} restarted successfully")
                    else:
                        self.logger.error(f"Failed to restart worker {worker_name}")
                    return success
                
                self.logger.error(f"Worker {worker_name} does not support restart")
                return False
                
            except Exception as e:
                self.logger.error(f"Failed to restart worker {worker_name}: {e}")
                return False 
