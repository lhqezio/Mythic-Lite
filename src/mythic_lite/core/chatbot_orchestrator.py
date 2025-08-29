"""
Main orchestrator module for Mythic-Lite chatbot system.

Coordinates all workers and manages the main chatbot interface.
"""

import time
import json
import os
from datetime import datetime
from typing import Optional, Any, Dict, List

from .conversation_worker import ConversationWorker
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
        self.conversation_worker = ConversationWorker(self.config)
        
        # Set LLM worker reference in memory worker
        self.memory_worker.set_llm_worker(self.llm_worker)
        
        # Debug mode from configuration
        self.debug_mode = self.config.debug_mode
        self.conversation_worker.debug_mode = self.debug_mode
        
        # Performance tracking
        self.start_time = time.time()
        self.total_conversations = 0
        self.benchmark_results = None  # Store benchmark test results
        
        # Track initialization status
        self._initialized = False
        
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
            
            # Initialize conversation worker
            self.logger.debug("Initializing conversation worker...")
            if not self.conversation_worker.initialize():
                self.logger.warning("Conversation worker initialization failed")
            else:
                self.logger.debug("Conversation worker initialized successfully")
            
            self._initialized = True
            self.logger.success("All workers initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workers: {e}")
            return False
    
    def _handle_speech_input(self, transcription: str):
        """Handle speech input from ASR worker."""
        try:
            self.logger.info(f"Speech input received: {transcription}")
            
            # Process the transcription through the conversation system
            response = self.conversation_worker.process_user_input(transcription)
            
            if response:
                # Speak the response
                self.tts_worker.speak(response)
                
                # Update conversation tracking
                self.total_conversations += 1
                
        except Exception as e:
            self.logger.error(f"Error processing speech input: {e}")
    
    def _handle_partial_speech(self, partial: str):
        """Handle partial speech input from ASR worker."""
        # For now, just log partial results at debug level
        if self.debug_mode:
            self.logger.debug(f"Partial speech: {partial}")
    
    def run_chatbot(self):
        """Run the chatbot in text mode."""
        if not self._initialized:
            if not self.initialize_workers():
                self.logger.error("Failed to initialize workers")
                return
        
        self.logger.info("Starting text-based chatbot...")
        
        try:
            while True:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self.logger.info("User requested to exit")
                    break
                
                if not user_input:
                    continue
                
                # Process input
                response = self.conversation_worker.process_user_input(user_input)
                
                if response:
                    print(f"Mythic: {response}")
                    
                    # Update conversation tracking
                    self.total_conversations += 1
                    
        except KeyboardInterrupt:
            self.logger.info("Chatbot interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in chatbot: {e}")
    
    def run_asr_only(self):
        """Run only the ASR system for voice input."""
        if not self._initialized:
            if not self.initialize_workers():
                self.logger.error("Failed to initialize workers")
                return
        
        if not self.asr_worker.is_recording_active():
            self.logger.info("Starting ASR-only mode...")
            
            # Start recording
            if self.asr_worker.start_recording():
                self.logger.info("ASR recording started. Speak to interact...")
                
                try:
                    # Keep running until interrupted
                    while self.asr_worker.is_recording_active():
                        time.sleep(0.1)
                        
                except KeyboardInterrupt:
                    self.logger.info("ASR mode interrupted by user")
                finally:
                    self.asr_worker.stop_recording()
            else:
                self.logger.error("Failed to start ASR recording")
    
    def run_voice_mode(self):
        """Run the chatbot in full voice mode."""
        if not self._initialized:
            if not self.initialize_workers():
                self.logger.error("Failed to initialize workers")
                return
        
        self.logger.info("Starting voice conversation mode...")
        
        try:
            # Start ASR
            if not self.asr_worker.start_recording():
                self.logger.error("Failed to start ASR")
                return
            
            self.logger.info("Voice mode active. Speak to interact...")
            
            # Keep running until interrupted
            while self.asr_worker.is_recording_active():
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Voice mode interrupted by user")
        finally:
            self.asr_worker.stop_recording()
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run system benchmark tests."""
        if not self._initialized:
            if not self.initialize_workers():
                self.logger.error("Failed to initialize workers")
                return {}
        
        self.logger.info("Starting system benchmark...")
        
        benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'llm_performance': {},
            'memory_performance': {},
            'tts_performance': {},
            'asr_performance': {},
            'overall_score': 0.0
        }
        
        try:
            # LLM benchmark
            self.logger.info("Running LLM benchmark...")
            llm_start = time.time()
            test_response = self.llm_worker.generate_response("Hello, how are you?")
            llm_time = time.time() - llm_start
            
            benchmark_results['llm_performance'] = {
                'response_time': llm_time,
                'response_length': len(test_response) if test_response else 0,
                'status': 'success' if test_response else 'failed'
            }
            
            # Memory benchmark
            self.logger.info("Running memory benchmark...")
            memory_start = time.time()
            memory_status = self.memory_worker.get_status()
            memory_time = time.time() - memory_start
            
            benchmark_results['memory_performance'] = {
                'initialization_time': memory_time,
                'status': 'success' if memory_status.get('initialized', False) else 'failed'
            }
            
            # TTS benchmark
            self.logger.info("Running TTS benchmark...")
            tts_start = time.time()
            tts_status = self.tts_worker.get_status()
            tts_time = time.time() - tts_start
            
            benchmark_results['tts_performance'] = {
                'status_check_time': tts_time,
                'status': 'success' if tts_status.get('worker_initialized', False) else 'failed'
            }
            
            # ASR benchmark
            self.logger.info("Running ASR benchmark...")
            asr_start = time.time()
            asr_status = self.asr_worker.get_status()
            asr_time = time.time() - asr_start
            
            benchmark_results['asr_performance'] = {
                'status_check_time': asr_time,
                'status': 'success' if asr_status.get('worker_initialized', False) else 'failed'
            }
            
            # Calculate overall score
            scores = []
            if benchmark_results['llm_performance']['status'] == 'success':
                scores.append(25.0)
            if benchmark_results['memory_performance']['status'] == 'success':
                scores.append(25.0)
            if benchmark_results['tts_performance']['status'] == 'success':
                scores.append(25.0)
            if benchmark_results['asr_performance']['status'] == 'success':
                scores.append(25.0)
            
            benchmark_results['overall_score'] = sum(scores)
            
            self.logger.success(f"Benchmark completed. Overall score: {benchmark_results['overall_score']}/100")
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")
        
        self.benchmark_results = benchmark_results
        return benchmark_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        if not self._initialized:
            return {'status': 'not_initialized'}
        
        status = {
            'status': 'running',
            'uptime': time.time() - self.start_time,
            'total_conversations': self.total_conversations,
            'workers': {
                'llm': self.llm_worker.get_status() if hasattr(self.llm_worker, 'get_status') else {},
                'memory': self.memory_worker.get_status() if hasattr(self.memory_worker, 'get_status') else {},
                'tts': self.tts_worker.get_status() if hasattr(self.tts_worker, 'get_status') else {},
                'asr': self.asr_worker.get_status() if hasattr(self.asr_worker, 'get_status') else {},
                'conversation': self.conversation_worker.get_status() if hasattr(self.conversation_worker, 'get_status') else {}
            },
            'configuration': {
                'debug_mode': self.debug_mode,
                'asr_enabled': self.config.asr.enable_asr,
                'tts_enabled': self.config.tts.enable_audio
            }
        }
        
        return status
    
    def cleanup(self):
        """Cleanup all resources."""
        self.logger.info("Cleaning up orchestrator resources...")
        
        try:
            # Cleanup workers
            if hasattr(self.tts_worker, 'cleanup'):
                self.tts_worker.cleanup()
            if hasattr(self.asr_worker, 'cleanup'):
                self.asr_worker.cleanup()
            if hasattr(self.llm_worker, 'cleanup'):
                self.llm_worker.cleanup()
            if hasattr(self.memory_worker, 'cleanup'):
                self.memory_worker.cleanup()
            if hasattr(self.conversation_worker, 'cleanup'):
                self.conversation_worker.cleanup()
            
            self._initialized = False
            self.logger.info("Orchestrator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        if not self._initialized:
            self.initialize_workers()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup() 
