"""
Automatic Speech Recognition Worker for Mythic-Lite chatbot system.

This module provides the ASR worker that coordinates with the audio engine
to handle speech recognition functionality.
"""

import time
import threading
import queue
from typing import Optional, Any, Callable, Dict
from pathlib import Path

from ..core.audio import ASREngine
from ..utils.logger import get_logger
from ..core.config import ASRConfig


class ASRWorker:
    """Worker class for handling automatic speech recognition."""
    
    def __init__(self, config: Optional[Any] = None):
        if config is None:
            raise ValueError("ASR worker requires a configuration object. All config must come from the main config file.")
        
        self.config = config.asr if hasattr(config, 'asr') else config
        self.logger = get_logger("asr-worker")
        
        # Initialize the ASR engine
        self.asr_engine = ASREngine(self.config)
        
        # Recording state
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.total_transcriptions = 0
        self.total_audio_processed = 0
        self.average_processing_time = 0.0
        
        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_partial: Optional[Callable[[str], None]] = None
    
    def initialize(self) -> bool:
        """Initialize the ASR worker."""
        try:
            if not self.asr_engine.initialize():
                self.logger.error("Failed to initialize ASR engine")
                return False
            
            self.logger.info("ASR worker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ASR worker: {e}")
            return False
    
    def set_callbacks(self, on_transcription: Optional[Callable[[str], None]] = None,
                     on_partial: Optional[Callable[[str], None]] = None):
        """Set callback functions for transcription events."""
        self.on_transcription = on_transcription
        self.on_partial = on_partial
        
        # Also set callbacks on the engine
        self.asr_engine.set_callbacks(on_transcription, on_partial)
    
    def start_recording(self) -> bool:
        """Start audio recording."""
        if not self.asr_engine.is_initialized:
            self.logger.error("ASR worker not initialized")
            return False
        
        if self.is_recording:
            self.logger.warning("Already recording")
            return True
        
        try:
            if self.asr_engine.start_recording():
                self.is_recording = True
                self.logger.info("Started audio recording with Vosk")
                return True
            else:
                self.logger.error("Failed to start recording")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop audio recording."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.asr_engine.stop_recording()
        self.logger.info("Stopped audio recording")
    
    def pause_recording(self):
        """Pause audio recording."""
        if not self.is_recording:
            return
        
        self.asr_engine.stop_recording()
        self.logger.debug("ASR paused - stopping audio collection")
    
    def resume_recording(self):
        """Resume audio recording."""
        if self.is_recording:
            return
        
        if self.asr_engine.start_recording():
            self.is_recording = True
            self.logger.debug("ASR resumed - resuming audio collection")
    
    def is_recording_active(self) -> bool:
        """Check if recording is currently active."""
        return self.is_recording and self.asr_engine.is_recording
    
    def transcribe_file(self, audio_file_path: str) -> Optional[str]:
        """Transcribe an audio file."""
        if not self.asr_engine.is_initialized:
            self.logger.error("ASR worker not initialized")
            return None
        
        try:
            self.logger.debug(f"Transcribing file: {audio_file_path}")
            transcription = self.asr_engine.transcribe_file(audio_file_path)
            
            if transcription:
                self.total_transcriptions += 1
                self.logger.debug(f"File transcription: {transcription}")
            
            return transcription
            
        except Exception as e:
            self.logger.error(f"Failed to transcribe file: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the ASR worker."""
        engine_status = self.asr_engine.get_status()
        
        return {
            'worker_initialized': self.asr_engine.is_initialized,
            'recording_active': self.is_recording,
            'total_transcriptions': self.total_transcriptions,
            'total_audio_processed': self.total_audio_processed,
            'average_processing_time': self.average_processing_time,
            **engine_status
        }
    
    def cleanup(self):
        """Cleanup ASR worker resources."""
        if self.asr_engine:
            self.asr_engine.cleanup()
        
        self.logger.info("ASR worker cleaned up")
