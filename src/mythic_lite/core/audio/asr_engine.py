"""
Automatic Speech Recognition Engine for Mythic-Lite chatbot system.

This module provides the core ASR functionality using Vosk,
separated from the worker implementation for better modularity.
"""

import os
import time
import threading
import queue
from typing import Optional, Any, Callable, Dict
from pathlib import Path

# Make Vosk import optional for testing
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    # Mock classes for testing
    class Model:
        def __init__(self, path):
            pass
    
    class KaldiRecognizer:
        def __init__(self, model, sample_rate):
            pass
        
        def AcceptWaveform(self, data):
            return True
        
        def Result(self):
            return '{"text": "mock transcription"}'
        
        def PartialResult(self):
            return '{"partial": "mock partial"}'
        
        def Reset(self):
            pass

# Make PyAudio import optional for testing
try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    # Mock classes for testing
    class MockPyAudio:
        def __init__(self):
            pass
        
        def open(self, **kwargs):
            return type('MockStream', (), {
                'read': lambda chunk: b'\x00' * chunk,
                'stop_stream': lambda: None,
                'close': lambda: None
            })()
        
        def terminate(self):
            pass
    
    pyaudio = MockPyAudio()
    np = None

from ...utils.logger import get_logger
from ...core.config import ASRConfig


class ASREngine:
    """Core ASR engine for automatic speech recognition."""
    
    def __init__(self, config: ASRConfig):
        self.config = config
        self.logger = get_logger("asr-engine")
        
        self.model: Optional[Model] = None
        self.recognizer: Optional[KaldiRecognizer] = None
        self.is_initialized: bool = False
        self.initialization_error: Optional[str] = None
        self.is_enabled: bool = False
        
        # Audio recording setup
        self.audio_stream: Optional[Any] = None
        self.is_recording: bool = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_queue: queue.Queue = queue.Queue()
        
        # PyAudio instance
        self.pyaudio: Optional[pyaudio.PyAudio] = None
        self._setup_pyaudio()
        
        # Performance tracking
        self.total_transcriptions: int = 0
        self.total_audio_processed: int = 0
        self.average_processing_time: float = 0.0
        
        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_partial: Optional[Callable[[str], None]] = None
    
    def _setup_pyaudio(self):
        """Setup PyAudio for audio recording."""
        if not AUDIO_AVAILABLE:
            self.logger.warning("PyAudio not available - audio recording disabled")
            self.pyaudio = None
            return
        
        try:
            self.pyaudio = pyaudio.PyAudio()
            self.logger.debug("PyAudio initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize PyAudio: {e}")
            self.pyaudio = None
    
    def initialize(self) -> bool:
        """Initialize the ASR engine."""
        if self.is_initialized:
            return True
        
        try:
            if not VOSK_AVAILABLE:
                self.logger.error("Vosk not available - ASR disabled")
                self.initialization_error = "Vosk not available"
                return False
            
            if not AUDIO_AVAILABLE:
                self.logger.error("PyAudio not available - ASR disabled")
                self.initialization_error = "PyAudio not available"
                return False
            
            # Load Vosk model
            model_path = self._get_model_path()
            if not model_path or not model_path.exists():
                self.logger.error(f"Vosk model not found: {model_path}")
                self.initialization_error = f"Vosk model not found: {model_path}"
                return False
            
            self.model = Model(str(model_path))
            self.recognizer = KaldiRecognizer(self.model, self.config.sample_rate)
            
            self.logger.info(f"Loaded Vosk model: {model_path}")
            
            self.is_initialized = True
            self.is_enabled = True
            self.initialization_error = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ASR engine: {e}")
            self.initialization_error = str(e)
            return False
    
    def _get_model_path(self) -> Optional[Path]:
        """Get the path to the Vosk model."""
        # This would need to be implemented based on your model structure
        # For now, return a default path
        return Path("models/vosk-model-small-en-us-0.15")
    
    def set_callbacks(self, on_transcription: Optional[Callable[[str], None]] = None,
                     on_partial: Optional[Callable[[str], None]] = None):
        """Set callback functions for transcription events."""
        self.on_transcription = on_transcription
        self.on_partial = on_partial
    
    def start_recording(self) -> bool:
        """Start audio recording."""
        if not self.is_initialized or not self.pyaudio:
            self.logger.error("ASR engine not initialized")
            return False
        
        if self.is_recording:
            self.logger.warning("Already recording")
            return True
        
        try:
            # Open audio stream
            self.audio_stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            self.is_recording = True
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
            self.recording_thread.start()
            
            self.logger.info("Started audio recording with Vosk")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop audio recording."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
        
        self.logger.info("Stopped audio recording")
    
    def _recording_loop(self):
        """Main recording loop that processes audio data."""
        while self.is_recording:
            try:
                if not self.audio_stream:
                    break
                
                # Read audio data
                data = self.audio_stream.read(1024, exception_on_overflow=False)
                
                if self.recognizer:
                    # Process with Vosk
                    if self.recognizer.AcceptWaveform(data):
                        result = self.recognizer.Result()
                        self._process_transcription(result)
                    else:
                        partial = self.recognizer.PartialResult()
                        self._process_partial(partial)
                
            except Exception as e:
                self.logger.error(f"Error in recording loop: {e}")
                break
    
    def _process_transcription(self, result: str):
        """Process a complete transcription result."""
        try:
            import json
            result_data = json.loads(result)
            text = result_data.get('text', '').strip()
            
            if text:
                self.total_transcriptions += 1
                self.logger.debug(f"Processing transcription: '{text}'")
                
                if self.on_transcription:
                    self.on_transcription(text)
                
                # Reset recognizer for next input
                if self.recognizer:
                    self.recognizer.Reset()
                
        except Exception as e:
            self.logger.error(f"Error processing transcription: {e}")
    
    def _process_partial(self, partial: str):
        """Process a partial transcription result."""
        try:
            import json
            partial_data = json.loads(partial)
            text = partial_data.get('partial', '').strip()
            
            if text and self.on_partial:
                self.on_partial(text)
                
        except Exception as e:
            self.logger.error(f"Error processing partial: {e}")
    
    def transcribe_file(self, audio_file_path: str) -> Optional[str]:
        """Transcribe an audio file."""
        if not self.is_initialized or not self.recognizer:
            self.logger.error("ASR engine not initialized")
            return None
        
        try:
            # This would need to be implemented based on your audio file format
            # For now, return a placeholder
            self.logger.debug(f"Transcribing file: {audio_file_path}")
            return "File transcription placeholder"
            
        except Exception as e:
            self.logger.error(f"Failed to transcribe file: {e}")
            return None
    
    def cleanup(self):
        """Cleanup ASR engine resources."""
        self.stop_recording()
        
        if self.pyaudio:
            self.pyaudio.terminate()
            self.pyaudio = None
        
        self.is_initialized = False
        self.is_enabled = False
        self.logger.info("ASR engine cleaned up")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the ASR engine."""
        return {
            'initialized': self.is_initialized,
            'enabled': self.is_enabled,
            'error': self.initialization_error,
            'recording': self.is_recording,
            'total_transcriptions': self.total_transcriptions,
            'total_audio_processed': self.total_audio_processed,
            'average_processing_time': self.average_processing_time,
            'vosk_available': VOSK_AVAILABLE,
            'audio_available': AUDIO_AVAILABLE
        }