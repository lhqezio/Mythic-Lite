"""
Text-to-Speech (TTS) Worker Module

This module provides text-to-speech functionality using Piper TTS.
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

from ..utils.logger import get_logger
from ..core.config import TTSConfig


class TTSWorker:
    """Worker class for handling text-to-speech functionality."""
    
    def __init__(self, config: Optional[Any] = None):
        if config is None:
            # Mock config for testing
            self.config = type('MockConfig', (), {
                'tts': type('MockTTSConfig', (), {
                    'voice_path': 'amy-low',
                    'sample_rate': 22050,
                    'channels': 1,
                    'audio_format': 'paInt16',
                    'enable_audio': True,
                    'AVAILABLE_VOICES': {
                        'amy-low': 'en/en_US/amy/low',
                        'amy-medium': 'en/en_US/amy/medium',
                        'amy-high': 'en/en_US/amy/high',
                        'jenny-low': 'en/en_US/jenny/low',
                        'jenny-medium': 'en/en_US/jenny/medium',
                        'jenny-high': 'en/en_US/jenny/high'
                    }
                })(),
                'debug_mode': False
            })()
        else:
            self.config = config
        
        self.logger = get_logger("tts-worker")
        
        self.voice: Optional[PiperVoice] = None
        self.is_initialized: bool = False
        self.initialization_error: Optional[str] = None
        self.is_enabled: bool = False  # Add the missing attribute
        
        # Audio streaming setup
        self.audio_queue: queue.Queue = queue.Queue()
        self.is_playing: bool = False
        self.audio_thread: Optional[threading.Thread] = None
        
        # Audio configuration
        self.sample_rate: int = self.config.tts.sample_rate
        self.channels: int = self.config.tts.channels
        self.audio_format: str = self.config.tts.audio_format
        
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
            self.logger.error(f"PyAudio initialization failed: {e}")
            self.logger.debug(f"PyAudio error details: {e}", exc_info=True)
            self.pyaudio = None
    
    def initialize(self) -> bool:
        """Initialize the TTS system."""
        try:
            self.logger.info("Initializing TTS system...")
            
            # Use lazy import to avoid circular dependencies
            from ..core.model_manager import ensure_model
            
            # Get the voice name from config
            voice_name = self.config.tts.voice_path
            
            # Map voice name to the correct Piper voice path
            if voice_name in self.config.tts.AVAILABLE_VOICES:
                voice_path = self.config.tts.AVAILABLE_VOICES[voice_name]
            else:
                # Fallback: assume it's already a full path
                voice_path = voice_name
            
            # Construct the full paths for both .onnx and .onnx.json files
            # The actual filenames include the en_US- prefix: en_US-amy-low.onnx
            tts_model_path = f"{voice_path}/en_US-{voice_name}.onnx"
            tts_json_path = f"{voice_path}/en_US-{voice_name}.onnx.json"
            
            self.logger.info(f"Downloading TTS model: {voice_name} from rhasspy/piper-voices")
            self.logger.info(f"Model path: {tts_model_path}")
            self.logger.info(f"Config path: {tts_json_path}")
            
            # Ensure both the .onnx and .onnx.json files are downloaded
            model_path = ensure_model(
                "tts",
                "rhasspy/piper-voices",
                tts_model_path
            )
            
            json_path = ensure_model(
                "tts",
                "rhasspy/piper-voices", 
                tts_json_path
            )
            
            if not model_path or not json_path:
                raise Exception("Failed to download TTS model files")
            
            # Initialize Piper voice using the .onnx file
            self.voice = PiperVoice.load(str(model_path))
            
            self.is_initialized = True
            self.is_enabled = True  # Enable TTS after successful initialization
            self.initialization_error = None
            
            self.logger.success("TTS system initialized successfully!")
            self.logger.info(f"Voice: {voice_name}")
            self.logger.info(f"Model: {model_path}")
            self.logger.info(f"Config: {json_path}")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.is_initialized = False
            return False
    
    def _find_voice_file(self) -> Optional[Path]:
        """Find the voice file in various locations."""
        try:
            # Try to ensure TTS model is downloaded
            # TTS models need both .onnx and .onnx.json files
            tts_base_name = self.config.tts.voice_path.replace('.onnx', '')
            tts_onnx_path = f"en/en_US/amy/low/{tts_base_name}.onnx"
            tts_json_path = f"en/en_US/amy/low/{tts_base_name}.onnx.json"
            
            # Download both files
            voice_path = ensure_model("tts", "rhasspy/piper-voices", tts_onnx_path)
            json_path = ensure_model("tts", "rhasspy/piper-voices", tts_json_path)
            
            if voice_path and voice_path.exists() and json_path and json_path.exists():
                self.logger.debug(f"Found TTS model files: {voice_path.name} and {json_path.name}")
                return voice_path
            else:
                self.logger.warning("TTS model files incomplete - missing .onnx or .onnx.json")
        except Exception as e:
            self.logger.warning(f"Failed to download TTS model: {e}")
        
        # Fallback to local search
        possible_paths = [
            # Current script directory
            Path(__file__).parent / self.config.tts.voice_path,
            # Configuration base path
            self.config.base_path / self.config.tts.voice_path,
            # Models directory
            self.config.get_model_path("tts") / self.config.tts.voice_path,
            # Current working directory
            Path.cwd() / self.config.tts.voice_path,
            # Absolute path if provided
            Path(self.config.tts.voice_path)
        ]
        
        for path in possible_paths:
            if path.exists():
                self.logger.debug(f"Found voice file at: {path}")
                return path
        
        self.logger.error("Voice file not found in any of these locations:")
        for path in possible_paths:
            self.logger.error(f"  - {path}")
        
        return None
    
    def text_to_speech_stream(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using Piper TTS with streaming.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes, or None if conversion failed
        """
        if not self.is_initialized or self.voice is None:
            self.logger.error("TTS not initialized. Cannot convert to speech.")
            return None
        
        if not self.config.tts.enable_audio:
            self.logger.debug("TTS disabled, skipping audio generation")
            return None
        
        try:
            # Clean text for TTS to avoid phoneme errors
            clean_text = self._clean_text_for_tts(text)
            if not clean_text:
                # Only warn for meaningful text that gets cleaned away, not punctuation
                if len(text.strip()) > 1 and not text.strip().isspace() and not all(char in '.,!?;:()[]{}"\'' for char in text.strip()):
                    self.logger.warning(f"Text cleaning resulted in empty text: '{text}'")
                else:
                    self.logger.debug(f"Skipping punctuation/short text for TTS: '{text}'")
                return None
            
            self.logger.debug(f"Generating TTS for text: '{clean_text}'")
            start_time = time.time()
            
            # Generate audio - handle AudioChunk objects from Piper TTS
            audio_result = self.voice.synthesize(clean_text)
            self.logger.debug(f"Voice.synthesize returned: {type(audio_result)}")
            
            # Check the type of result and handle accordingly
            if hasattr(audio_result, '__iter__') and not isinstance(audio_result, (bytes, bytearray)):
                # It's an iterable (generator or list), handle AudioChunk objects
                self.logger.debug("Audio result is iterable, processing chunks...")
                audio_chunks = []
                
                for chunk in audio_result:
                    try:
                        self.logger.debug(f"Processing chunk type: {type(chunk)}")
                        # AudioChunk has audio_int16_bytes which contains the actual audio data
                        if hasattr(chunk, 'audio_int16_bytes'):
                            # This is the correct attribute for AudioChunk
                            audio_bytes = chunk.audio_int16_bytes
                            self.logger.debug(f"AudioChunk.audio_int16_bytes type: {type(audio_bytes)}")
                            if isinstance(audio_bytes, bytes):
                                audio_chunks.append(audio_bytes)
                                self.logger.debug(f"Added audio chunk: {len(audio_bytes)} bytes")
                            else:
                                self.logger.warning(f"audio_int16_bytes is not bytes: {type(audio_bytes)}")
                                continue
                        elif hasattr(chunk, 'audio_float_array'):
                            # Alternative: convert float array to int16 bytes
                            import numpy as np
                            try:
                                float_array = chunk.audio_float_array
                                # Convert float32 to int16 (typical for audio)
                                int16_array = (float_array * 32767).astype(np.int16)
                                audio_chunks.append(int16_array.tobytes())
                                self.logger.debug(f"Converted float array to int16: {len(audio_chunks[-1])} bytes")
                            except Exception as e:
                                self.logger.warning(f"Could not convert float array: {e}")
                                continue
                        elif hasattr(chunk, 'tobytes'):
                            # Direct tobytes method
                            audio_chunks.append(chunk.tobytes())
                            self.logger.debug(f"Direct tobytes: {len(audio_chunks[-1])} bytes")
                        elif isinstance(chunk, (bytes, bytearray)):
                            # Already bytes
                            audio_chunks.append(chunk)
                            self.logger.debug(f"Already bytes: {len(chunk)} bytes")
                        else:
                            # Last resort: try to convert to numpy array
                            import numpy as np
                            try:
                                np_array = np.array(chunk)
                                audio_chunks.append(np_array.tobytes())
                                self.logger.debug(f"Converted chunk to numpy: {len(audio_chunks[-1])} bytes")
                            except:
                                self.logger.warning(f"Could not convert AudioChunk to audio data: {type(chunk)}")
                                continue
                    except Exception as e:
                        self.logger.debug(f"Error processing audio chunk: {e}")
                        continue
                
                # Combine all audio chunks
                if audio_chunks:
                    audio_data = b''.join(audio_chunks)
                    self.logger.debug(f"Combined {len(audio_chunks)} audio chunks into {len(audio_data)} bytes")
                else:
                    self.logger.error("No valid audio chunks generated")
                    # Disable TTS to prevent further errors
                    self.logger.warning("Disabling TTS due to audio generation failures")
                    self.is_enabled = False
                    return None
            else:
                # It's bytes, use directly
                self.logger.debug("Audio result is bytes, using directly")
                audio_data = audio_result
            
            # Update performance metrics
            generation_time = time.time() - start_time
            self._update_performance_metrics(len(audio_data), generation_time)
            
            self.logger.debug(f"Generated {len(audio_data)} bytes of audio in {generation_time:.2f}s")
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Error in TTS: {e}")
            self.logger.debug(f"TTS error details: {e}", exc_info=True)
            # Disable TTS to prevent further errors
            self.logger.warning("Disabling TTS due to error")
            self.is_enabled = False
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for TTS processing."""
        if not text:
            return ""
        
        # Remove any remaining prompt artifacts that might cause TTS issues
        clean_text = text.strip()
        clean_text = clean_text.replace('</s>', '').replace('<s>', '').replace('<|', '').replace('|>', '')
        clean_text = clean_text.replace('  ', ' ').strip()  # Remove double spaces
        
        # Remove very short text that might cause TTS issues
        if len(clean_text) < 2:
            return ""
        
        # Remove chunks that are only punctuation or whitespace
        if clean_text and clean_text.strip().isspace():
            return ""
        
        # Remove chunks that are only punctuation marks
        if clean_text and all(char in '.,!?;:()[]{}"\'' for char in clean_text.strip()):
            return ""
        
        return clean_text
    
    def start_audio_player(self):
        """Start the background audio player thread."""
        if self.pyaudio is None:
            self.logger.warning("PyAudio not available, cannot start audio player")
            return
        
        if self.is_playing:
            self.logger.debug("Audio player already running")
            return
        
        self.is_playing = True
        self.audio_thread = threading.Thread(target=self._audio_player_thread, daemon=True)
        self.audio_thread.start()
        self.logger.debug("Audio player thread started")
    
    def _audio_player_thread(self):
        """Background thread for playing audio from the queue."""
        try:
            while self.is_playing:
                try:
                    # Get audio data from queue with timeout
                    audio_data = self.audio_queue.get(timeout=0.1)
                    if audio_data:
                        self._play_audio_data(audio_data)
                except queue.Empty:
                    # Queue is empty, but keep the thread alive for future audio
                    # Only exit if explicitly stopped
                    continue
                except Exception as e:
                    # During shutdown, some errors are expected
                    if self.is_playing:
                        self.logger.error(f"Error in audio player thread: {e}")
                        self.logger.debug(f"Audio player error details: {e}", exc_info=True)
                    else:
                        # Shutdown in progress, just log as debug
                        self.logger.debug(f"Audio player thread error during shutdown: {e}")
        except Exception as e:
            # During shutdown, some errors are expected
            if self.is_playing:
                self.logger.error(f"Fatal error in audio player thread: {e}")
                self.logger.debug(f"Fatal audio player error details: {e}", exc_info=True)
            else:
                self.logger.debug(f"Audio player thread fatal error during shutdown: {e}")
        finally:
            # Set is_playing to False when thread exits
            self.is_playing = False
            self.logger.debug("Audio player thread stopped")
    
    def _play_audio_data(self, audio_data: bytes):
        """Play audio data using PyAudio."""
        stream = None
        try:
            # Check if we're still supposed to be playing
            if not self.is_playing:
                return
            
            # Open stream and play audio directly
            stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Check again before playing
            if not self.is_playing:
                return
            
            # Play audio data directly without wave file conversion
            # This preserves the original audio quality
            stream.write(audio_data)
            
        except Exception as e:
            # During shutdown, some errors are expected
            if self.is_playing:
                self.logger.error(f"Error playing audio: {e}")
                self.logger.debug(f"Audio playback error details: {e}", exc_info=True)
            else:
                self.logger.debug(f"Audio playback error during shutdown: {e}")
        finally:
            # Always try to close the stream
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    # Stream closure errors during shutdown are expected
                    if self.is_playing:
                        self.logger.debug(f"Error closing audio stream: {e}")
    
    def play_audio_stream(self, audio_data):
        """Queue audio data for playback. Handles both bytes and generators."""
        if not self.is_playing:
            self.logger.warning("Audio player not running, starting it now")
            self.start_audio_player()
        
        try:
            # Handle generator objects by consuming them
            if hasattr(audio_data, '__iter__') and not isinstance(audio_data, (bytes, bytearray)):
                # It's a generator, consume it and queue the audio data
                for chunk in audio_data:
                    if chunk and len(chunk) > 0:
                        self.audio_queue.put(chunk)
                        self.logger.debug(f"Queued {len(chunk)} bytes of audio chunk for playback")
            else:
                # It's bytes, queue directly
                if audio_data and len(audio_data) > 0:
                    self.audio_queue.put(audio_data)
                    self.logger.debug(f"Queued {len(audio_data)} bytes of audio for playback")
                else:
                    self.logger.warning("Received empty audio data")
                    
        except Exception as e:
            self.logger.error(f"Error queuing audio: {e}")
            self.logger.debug(f"Audio queuing error details: {e}", exc_info=True)
    
    def stop_audio_player(self):
        """Stop the background audio player thread."""
        if not self.is_playing:
            return
        
        # Clear any remaining audio in the queue to prevent playback during shutdown
        try:
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()
        except:
            pass
        
        self.is_playing = False
        
        if self.audio_thread and self.audio_thread.is_alive():
            # Give the thread a chance to stop gracefully
            self.audio_thread.join(timeout=1.0)  # Reduced timeout for faster shutdown
            if self.audio_thread.is_alive():
                # Thread is still alive, but this is not critical
                self.logger.debug("Audio player thread still running (this is normal)")
        
        self.audio_thread = None
        self.logger.debug("Audio player stopped")
    
    def has_audio_playing(self) -> bool:
        """Check if there's actually audio playing or queued."""
        # Check if there's audio in the queue (more reliable than just is_playing)
        return not self.audio_queue.empty()
    
    def verify_audio_output(self) -> bool:
        """Verify that audio output is working."""
        if not self.pyaudio:
            self.logger.warning("PyAudio not available, cannot verify audio output")
            return False
        
        try:
            # List available audio output devices
            output_devices = []
            for i in range(self.pyaudio.get_device_count()):
                device_info = self.pyaudio.get_device_info_by_index(i)
                if device_info['maxOutputChannels'] > 0:
                    output_devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxOutputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
            
            if output_devices:
                self.logger.info(f"Found {len(output_devices)} audio output devices")
                for device in output_devices:
                    self.logger.debug(f"  Device {device['index']}: {device['name']}")
                return True
            else:
                self.logger.warning("No audio output devices found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying audio output: {e}")
            self.logger.debug(f"Audio verification error details: {e}", exc_info=True)
            return False
    
    def get_status(self) -> str:
        """Get the status of the TTS worker."""
        if self.is_initialized and self.is_enabled:
            return f"TTS: Piper Voice (Loaded & Ready) - {self.sample_rate}Hz"
        elif self.is_initialized and not self.is_enabled:
            return f"TTS: Piper Voice (Loaded but Disabled due to errors) - {self.sample_rate}Hz"
        elif self.initialization_error:
            return f"TTS: Failed to initialize - {self.initialization_error}"
        else:
            return "TTS: Not initialized"
    
    def is_tts_enabled(self) -> bool:
        """Check if TTS is enabled and working."""
        return self.is_initialized and self.is_enabled
    
    def re_enable_tts(self) -> bool:
        """Re-enable TTS if it was disabled due to errors."""
        if not self.is_initialized:
            self.logger.warning("Cannot re-enable TTS - not initialized")
            return False
        
        if self.is_enabled:
            self.logger.info("TTS is already enabled")
            return True
        
        try:
            # Try to reinitialize the voice
            self.logger.info("Attempting to re-enable TTS...")
            self.is_enabled = True
            
            # Test with a simple text to see if it works
            test_result = self.text_to_speech_stream("test")
            if test_result:
                self.logger.success("TTS re-enabled successfully!")
                return True
            else:
                self.logger.warning("TTS test failed after re-enabling")
                self.is_enabled = False
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to re-enable TTS: {e}")
            self.is_enabled = False
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "total_requests": self.total_requests,
            "total_audio_generated": self.total_audio_generated,
            "average_generation_time": self.average_generation_time,
            "is_initialized": self.is_initialized,
            "audio_player_running": self.is_playing
        }
    
    def _update_performance_metrics(self, audio_bytes: int, generation_time: float):
        """Update performance tracking metrics."""
        self.total_requests += 1
        self.total_audio_generated += audio_bytes
        
        # Update running average
        if self.total_requests == 1:
            self.average_generation_time = generation_time
        else:
            self.average_generation_time = (
                (self.average_generation_time * (self.total_requests - 1) + generation_time) 
                / self.total_requests
            )
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Stop audio player first
            self.stop_audio_player()
            
            # Clear any remaining audio data
            try:
                while not self.audio_queue.empty():
                    self.audio_queue.get_nowait()
            except:
                pass
            
            # Terminate PyAudio gracefully
            if self.pyaudio:
                try:
                    # Close any open streams first
                    self.pyaudio.terminate()
                    self.pyaudio = None
                except Exception as e:
                    self.logger.debug(f"PyAudio termination error (non-critical): {e}")
            
            # Clear other resources
            self.voice = None
            self.is_initialized = False
            self.is_enabled = False
            
            self.logger.info("TTS worker cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during TTS cleanup: {e}")
            self.logger.debug(f"TTS cleanup error details: {e}", exc_info=True)

    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it immediately.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            self.logger.error("TTS not initialized")
            return False
        
        if not self.config.tts.enable_audio:
            self.logger.debug("TTS disabled, skipping audio generation")
            return False
        
        try:
            self.logger.info(f"Speaking: {text[:50]}...")
            
            # Generate audio
            audio_data = self.text_to_speech_stream(text)
            if not audio_data:
                self.logger.error("Failed to generate audio")
                return False
            
            # Start audio player if not running
            if not self.is_playing:
                self.start_audio_player()
            
            # Queue audio for playback
            self.play_audio_stream(audio_data)
            
            self.logger.success("Audio queued for playback")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in speak: {e}")
            return False
    
    def speak_and_wait(self, text: str, timeout: float = 10.0) -> bool:
        """
        Convert text to speech, play it, and wait for completion.
        
        Args:
            text: Text to speak
            timeout: Maximum time to wait for playback to complete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.speak(text):
            return False
        
        # Wait for audio to finish playing
        start_time = time.time()
        while self.has_audio_playing() and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        return True
