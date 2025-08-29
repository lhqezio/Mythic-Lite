"""
Audio Stream for Mythic-Lite chatbot system.

This module provides audio streaming functionality for real-time
audio processing and playback.
"""

import threading
import queue
import time
from typing import Optional, Callable, Any
from collections import deque

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
                'write': lambda data: None,
                'read': lambda chunk: b'\x00' * chunk,
                'stop_stream': lambda: None,
                'close': lambda: None
            })()
        
        def terminate(self):
            pass
    
    pyaudio = MockPyAudio()
    np = None


class AudioStream:
    """Real-time audio streaming and buffering."""
    
    def __init__(self, sample_rate: int = 22050, channels: int = 1, 
                 chunk_size: int = 1024, buffer_size: int = 10):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size
        
        # Audio buffers
        self.input_buffer = deque(maxlen=buffer_size)
        self.output_buffer = deque(maxlen=buffer_size)
        
        # PyAudio instance
        self.pyaudio: Optional[pyaudio.PyAudio] = None
        self.input_stream: Optional[Any] = None
        self.output_stream: Optional[Any] = None
        
        # Streaming state
        self.is_streaming = False
        self.streaming_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_audio_input: Optional[Callable[[bytes], None]] = None
        self.on_audio_output: Optional[Callable[[bytes], None]] = None
        
        # Performance tracking
        self.total_input_chunks = 0
        self.total_output_chunks = 0
        self.latency_ms = 0.0
        
        self._setup_pyaudio()
    
    def _setup_pyaudio(self):
        """Setup PyAudio for audio streaming."""
        if not AUDIO_AVAILABLE:
            return
        
        try:
            self.pyaudio = pyaudio.PyAudio()
        except Exception as e:
            self.pyaudio = None
    
    def set_callbacks(self, on_input: Optional[Callable[[bytes], None]] = None,
                     on_output: Optional[Callable[[bytes], None]] = None):
        """Set callback functions for audio events."""
        self.on_audio_input = on_input
        self.on_audio_output = on_output
    
    def start_streaming(self) -> bool:
        """Start audio streaming."""
        if not self.pyaudio or self.is_streaming:
            return False
        
        try:
            # Open input stream
            self.input_stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Open output stream
            self.output_stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_streaming = True
            
            # Start streaming thread
            self.streaming_thread = threading.Thread(target=self._streaming_loop, daemon=True)
            self.streaming_thread.start()
            
            return True
            
        except Exception as e:
            self.stop_streaming()
            return False
    
    def stop_streaming(self):
        """Stop audio streaming."""
        self.is_streaming = False
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        
        if self.streaming_thread and self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=1.0)
    
    def _streaming_loop(self):
        """Main streaming loop for processing audio."""
        while self.is_streaming:
            try:
                # Read input audio
                if self.input_stream:
                    input_data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)
                    self._process_input_audio(input_data)
                
                # Process output audio
                if self.output_buffer:
                    output_data = self.output_buffer.popleft()
                    if self.output_stream:
                        self.output_stream.write(output_data)
                    self._process_output_audio(output_data)
                
                # Small delay to prevent busy waiting
                time.sleep(0.001)
                
            except Exception as e:
                break
        
        self.stop_streaming()
    
    def _process_input_audio(self, audio_data: bytes):
        """Process incoming audio data."""
        self.total_input_chunks += 1
        self.input_buffer.append(audio_data)
        
        if self.on_audio_input:
            self.on_audio_input(audio_data)
    
    def _process_output_audio(self, audio_data: bytes):
        """Process outgoing audio data."""
        self.total_output_chunks += 1
        
        if self.on_audio_output:
            self.on_audio_output(audio_data)
    
    def write_audio(self, audio_data: bytes) -> bool:
        """Write audio data to the output buffer."""
        if not self.is_streaming:
            return False
        
        try:
            self.output_buffer.append(audio_data)
            return True
        except Exception:
            return False
    
    def read_audio(self) -> Optional[bytes]:
        """Read audio data from the input buffer."""
        if not self.input_buffer:
            return None
        
        try:
            return self.input_buffer.popleft()
        except IndexError:
            return None
    
    def get_buffer_status(self) -> dict:
        """Get the current status of audio buffers."""
        return {
            'input_buffer_size': len(self.input_buffer),
            'output_buffer_size': len(self.output_buffer),
            'total_input_chunks': self.total_input_chunks,
            'total_output_chunks': self.total_output_chunks,
            'is_streaming': self.is_streaming
        }
    
    def set_buffer_size(self, size: int):
        """Set the buffer size for audio processing."""
        self.buffer_size = max(1, size)
        self.input_buffer = deque(maxlen=self.buffer_size)
        self.output_buffer = deque(maxlen=self.buffer_size)
    
    def clear_buffers(self):
        """Clear all audio buffers."""
        self.input_buffer.clear()
        self.output_buffer.clear()
    
    def cleanup(self):
        """Cleanup audio stream resources."""
        self.stop_streaming()
        
        if self.pyaudio:
            self.pyaudio.terminate()
            self.pyaudio = None