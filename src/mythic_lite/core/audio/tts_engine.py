"""
Text-to-Speech Engine for Mythic-Lite chatbot system.

This module provides the core TTS functionality using Piper TTS,
separated from the worker implementation for better modularity.
"""

import os
import tempfile
import time
import threading
import queue
from typing import Optional, Any, Union, Dict
from pathlib import Path

# Make audio imports optional for testing
try:
    import pyaudio
    import numpy as np
    from piper import PiperVoice
    # Try to import scipy for audio processing
    try:
        from scipy import signal
        SCIPY_AVAILABLE = True
    except ImportError:
        SCIPY_AVAILABLE = False
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    # Mock classes for testing
    class PiperVoice:
        @staticmethod
        def load(path):
            return type('MockPiperVoice', (), {})()
    
    class MockPyAudio:
        def __init__(self):
            pass
        
        def open(self, **kwargs):
            return type('MockStream', (), {
                'write': lambda data: None,
                'stop_stream': lambda: None,
                'close': lambda: None
            })()
        
        def terminate(self):
            pass
    
    pyaudio = MockPyAudio()
    np = None
    SCIPY_AVAILABLE = False

from ...utils.logger import get_logger
from ...core.config import TTSConfig


class TTSEngine:
    """Core TTS engine for text-to-speech functionality."""
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.logger = get_logger("tts-engine")
        
        self.voice: Optional[PiperVoice] = None
        self.is_initialized: bool = False
        self.initialization_error: Optional[str] = None
        self.is_enabled: bool = False
        
        # Audio streaming setup
        self.audio_queue: queue.Queue = queue.Queue()
        self.is_playing: bool = False
        self.audio_thread: Optional[threading.Thread] = None
        
        # Audio configuration
        self.sample_rate: int = self.config.sample_rate
        self.channels: int = self.config.channels
        self.audio_format: str = self.config.audio_format
        
        # Initialize PyAudio for real-time playback
        self.pyaudio: Optional[pyaudio.PyAudio] = None
        self._setup_pyaudio()
        
        # Performance tracking
        self.total_requests: int = 0
        self.total_audio_generated: int = 0
        self.average_generation_time: float = 0.0
        
        # Debug flag to avoid spamming unknown audio type logs
        self._unsupported_audio_logged: bool = False
    
    def _setup_pyaudio(self):
        """Setup PyAudio for audio playback."""
        if not AUDIO_AVAILABLE:
            self.logger.warning("PyAudio not available - audio playback disabled")
            self.pyaudio = None
            return
        
        try:
            self.pyaudio = pyaudio.PyAudio()
            self.logger.debug("PyAudio initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize PyAudio: {e}")
            self.pyaudio = None
    
    def initialize(self) -> bool:
        """Initialize the TTS engine."""
        if self.is_initialized:
            return True
        
        try:
            if not AUDIO_AVAILABLE:
                self.logger.warning("Audio libraries not available - TTS disabled")
                self.initialization_error = "Audio libraries not available"
                return False
            
            # Load Piper voice
            voice_path = self._get_voice_path()
            if not voice_path or not voice_path.exists():
                self.logger.error(f"Voice path not found: {voice_path}")
                self.initialization_error = f"Voice path not found: {voice_path}"
                return False
            
            self.voice = PiperVoice.load(str(voice_path))
            self.logger.info(f"Loaded Piper voice: {voice_path}")
            
            self.is_initialized = True
            self.is_enabled = True
            self.initialization_error = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.initialization_error = str(e)
            return False
    
    def _get_voice_path(self) -> Optional[Path]:
        """Get the path to the voice model."""
        voice_name = self.config.voice_path
        
        # Check if it's a full path
        if os.path.isabs(voice_name) or voice_name.startswith('./'):
            return Path(voice_name)
        
        # Check if it's in the available voices
        if voice_name in self.config.AVAILABLE_VOICES:
            # This would need to be implemented based on your voice model structure
            # For now, return the voice name as a path
            return Path(voice_name)
        
        # Default fallback
        return Path("ljspeech-high")
    
    def synthesize_speech(self, text: str) -> Optional[bytes]:
        """Synthesize speech from text."""
        if not self.is_initialized or not self.voice:
            self.logger.error("TTS engine not initialized")
            return None
        
        try:
            start_time = time.time()
            
            # Generate audio using Piper
            audio_data = self.voice.synthesize(text)
            
            generation_time = time.time() - start_time
            
            # Update performance metrics
            self.total_requests += 1
            self.total_audio_generated += len(audio_data)
            self.average_generation_time = (
                (self.average_generation_time * (self.total_requests - 1) + generation_time) 
                / self.total_requests
            )
            
            self.logger.debug(f"Generated {len(audio_data)} bytes of audio in {generation_time:.3f}s")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Failed to synthesize speech: {e}")
            return None
    
    def play_audio(self, audio_data: bytes) -> bool:
        """Play audio data through the speakers."""
        if not self.pyaudio or not AUDIO_AVAILABLE:
            self.logger.warning("Audio playback not available")
            return False
        
        try:
            # Convert audio data to numpy array if possible
            if np is not None:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            else:
                audio_array = audio_data
            
            # Open audio stream
            stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Play audio
            stream.write(audio_data)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
            return False
    
    def cleanup(self):
        """Cleanup TTS engine resources."""
        if self.pyaudio:
            self.pyaudio.terminate()
            self.pyaudio = None
        
        self.is_initialized = False
        self.is_enabled = False
        self.logger.info("TTS engine cleaned up")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the TTS engine."""
        return {
            'initialized': self.is_initialized,
            'enabled': self.is_enabled,
            'error': self.initialization_error,
            'total_requests': self.total_requests,
            'total_audio_generated': self.total_audio_generated,
            'average_generation_time': self.average_generation_time,
            'audio_available': AUDIO_AVAILABLE
        }