"""
Text-to-Speech Worker for Mythic-Lite chatbot system.

This module provides the TTS worker that coordinates with the audio engine
to handle text-to-speech functionality.
"""

import time
import threading
import queue
from typing import Optional, Any, Dict
from pathlib import Path

from ..core.audio import TTSEngine
from ..utils.logger import get_logger
from ..core.config import TTSConfig


class TTSWorker:
    """Worker class for handling text-to-speech functionality."""
    
    def __init__(self, config: Optional[Any] = None):
        if config is None:
            raise ValueError("TTS worker requires a configuration object. All config must come from the main config file.")
        
        self.config = config.tts if hasattr(config, 'tts') else config
        self.logger = get_logger("tts-worker")
        
        # Initialize the TTS engine
        self.tts_engine = TTSEngine(self.config)
        
        # Audio streaming setup
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.audio_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.total_requests = 0
        self.total_audio_generated = 0
        self.average_generation_time = 0.0
        
        # Debug flag to avoid spamming unknown audio type logs
        self._unsupported_audio_logged = False
    
    def initialize(self) -> bool:
        """Initialize the TTS worker."""
        try:
            if not self.tts_engine.initialize():
                self.logger.error("Failed to initialize TTS engine")
                return False
            
            self.logger.info("TTS worker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS worker: {e}")
            return False
    
    def speak(self, text: str, wait_for_completion: bool = True) -> bool:
        """Convert text to speech and play it."""
        if not self.tts_engine.is_initialized:
            self.logger.error("TTS worker not initialized")
            return False
        
        try:
            start_time = time.time()
            
            # Synthesize speech
            audio_data = self.tts_engine.synthesize_speech(text)
            if not audio_data:
                self.logger.error("Failed to synthesize speech")
                return False
            
            # Play audio
            if not self.tts_engine.play_audio(audio_data):
                self.logger.error("Failed to play audio")
                return False
            
            # Update performance metrics
            generation_time = time.time() - start_time
            self.total_requests += 1
            self.total_audio_generated += len(audio_data)
            self.average_generation_time = (
                (self.average_generation_time * (self.total_requests - 1) + generation_time) 
                / self.total_requests
            )
            
            self.logger.debug(f"Generated and played {len(audio_data)} bytes of audio in {generation_time:.3f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to speak text: {e}")
            return False
    
    def speak_async(self, text: str) -> bool:
        """Convert text to speech asynchronously."""
        try:
            # Start async playback thread
            self.audio_thread = threading.Thread(target=self._async_speak, args=(text,), daemon=True)
            self.audio_thread.start()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start async speech: {e}")
            return False
    
    def _async_speak(self, text: str):
        """Async speech processing."""
        try:
            self.speak(text, wait_for_completion=False)
        except Exception as e:
            self.logger.error(f"Async speech failed: {e}")
    
    def stop_speaking(self):
        """Stop any ongoing speech."""
        # This would need to be implemented based on your audio system
        # For now, just log the request
        self.logger.info("Stop speaking requested")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the TTS worker."""
        engine_status = self.tts_engine.get_status()
        
        return {
            'worker_initialized': self.tts_engine.is_initialized,
            'total_requests': self.total_requests,
            'total_audio_generated': self.total_audio_generated,
            'average_generation_time': self.average_generation_time,
            'is_playing': self.is_playing,
            **engine_status
        }
    
    def cleanup(self):
        """Cleanup TTS worker resources."""
        if self.tts_engine:
            self.tts_engine.cleanup()
        
        self.logger.info("TTS worker cleaned up")
