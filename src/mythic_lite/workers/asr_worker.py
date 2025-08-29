"""
ASR Worker for Mythic-Lite chatbot system.
Handles automatic speech recognition using lightweight vosk library (offline).
"""

import threading
import time
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import numpy as np
import pyaudio
import vosk

# Remove circular imports - don't import from core
# from ..core.config import get_config
# from ..core.model_manager import get_model_manager
from ..utils.logger import get_logger


class ASRWorker:
    """Worker for handling Automatic Speech Recognition tasks using vosk."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the ASR worker."""
        if config is None:
            raise ValueError("ASR worker requires a configuration object. All config must come from the main config file.")
        
        self.config = config
        
        self.logger = get_logger(__name__)
        
        # Audio recording settings
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.recording_thread = None
        
        # Vosk model
        self.model = None
        self.rec = None
        
        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_listening: Optional[Callable[[bool], None]] = None
        
        # State tracking
        self._last_transcription: Optional[str] = None
        self._recording_paused = False
        self._processing_state = False
        
        # Initialize Vosk model
        self._load_model()
    
    def _load_model(self):
        """Load the Vosk model using the model manager."""
        try:
            # Use lazy import to avoid circular dependencies
            from ..core.model_manager import get_model_manager
            
            # Use model manager to ensure Vosk model is available
            model_manager = get_model_manager()
            model_path = model_manager.ensure_vosk_model()
            
            if model_path and model_path.exists():
                self.model = vosk.Model(str(model_path))
                self.logger.info(f"Loaded Vosk model from: {model_path}")
                
                # Create recognizer
                self.rec = vosk.KaldiRecognizer(self.model, 16000)
                self.logger.info("Vosk ASR initialized successfully")
            else:
                self.logger.error("Failed to download Vosk model via model manager")
                self.logger.info("The model manager will automatically download the Vosk model on first run")
                self.model = None
                self.rec = None
                
        except Exception as e:
            self.logger.error(f"Failed to load Vosk model: {e}")
            self.logger.info("The model manager will automatically download the Vosk model on first run")
            self.model = None
            self.rec = None
    
    def set_callbacks(self, on_transcription: Callable[[str], None], 
                     on_error: Optional[Callable[[str], None]] = None,
                     on_listening: Optional[Callable[[bool], None]] = None):
        """Set callback functions for transcription, error handling, and listening status."""
        self.on_transcription = on_transcription
        self.on_error = on_error
        self.on_listening = on_listening
    
    def start_recording(self) -> bool:
        """Start recording audio for speech recognition."""
        if not self.rec:
            self.logger.error("Vosk model not loaded")
            return False
        
        if self.is_recording:
            self.logger.warning("Already recording")
            return False
        
        try:
            # Configure audio stream (following official Vosk example)
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,  # Mono for better recognition
                rate=16000,  # 16kHz for Vosk
                input=True,
                frames_per_buffer=4000  # 0.25 seconds at 16kHz (like official example)
            )
            
            self.is_recording = True
            self.logger.info("🎤 Started audio recording with Vosk")
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Notify that we're listening
            if self.on_listening:
                self.on_listening(True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording audio."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                self.logger.debug(f"Error closing audio stream: {e}")
            finally:
                self.stream = None
        
        if self.recording_thread and self.recording_thread.is_alive():
            # Give the recording thread time to finish gracefully
            self.recording_thread.join(timeout=2.0)
            if self.recording_thread.is_alive():
                self.logger.debug("Recording thread still running (this is normal)")
        
        self.recording_thread = None
        self.logger.info("🎤 Stopped audio recording")
    
    def pause_recording(self):
        """Pause recording temporarily without stopping the stream."""
        if self.is_recording:
            self._recording_paused = True
            self.logger.debug("🎤 ASR paused - stopping audio collection")
    
    def resume_recording(self):
        """Resume recording after being paused."""
        if self.is_recording:
            self._recording_paused = False
            self.logger.debug("🎤 ASR resumed - resuming audio collection")
    
    def is_paused(self) -> bool:
        """Check if recording is currently paused."""
        return self._recording_paused
    
    def is_processing(self) -> bool:
        """Check if currently processing audio."""
        return self._processing_state
    
    def get_speech_detection_status(self) -> Dict[str, Any]:
        """Get current speech detection status for debugging."""
        return {
            "status": "listening",
            "model_loaded": self.model is not None,
            "recognizer_ready": self.rec is not None,
            "sample_rate": 16000,
            "channels": 1
        }
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio input devices for debugging."""
        devices = {}
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # Input device
                    devices[f"Device {i}"] = {
                        "name": device_info['name'],
                        "max_input_channels": device_info['maxInputChannels'],
                        "default_sample_rate": device_info['defaultSampleRate'],
                        "host_api": device_info['hostApi']
                    }
        except Exception as e:
            self.logger.error(f"Failed to get audio devices: {e}")
        
        return devices
    
    def _recording_loop(self):
        """Main recording loop using Vosk for real-time recognition."""
        while self.is_recording:
            try:
                # Skip if paused
                if self._recording_paused:
                    time.sleep(0.1)
                    continue
                
                # Read audio data in smaller chunks (like the official example)
                data = self.stream.read(4000, exception_on_overflow=False)
                
                if self.rec.AcceptWaveform(data):
                    # Process the result
                    result = json.loads(self.rec.Result())
                    if result.get("text", "").strip():
                        transcription = result["text"].strip()
                        self._last_transcription = transcription
                        
                        # Debug: Log that we're processing a transcription
                        self.logger.debug(f"🎤 Processing transcription: '{transcription}'")
                        
                        if self.on_transcription:
                            # Call the callback without logging to avoid duplicate output
                            try:
                                self.on_transcription(transcription)
                                # Debug: Log that callback completed
                                self.logger.debug("🎤 Transcription callback completed, continuing to listen...")
                                
                                # Reset the recognizer to continue listening for new input
                                # This ensures Vosk can process new audio after transcription
                                self.rec = vosk.KaldiRecognizer(self.model, 16000)
                                self.logger.debug("🎤 Vosk recognizer reset for next input")
                            except Exception as e:
                                self.logger.error(f"Error in transcription callback: {e}")
                
                # Check for partial results (real-time feedback)
                partial = json.loads(self.rec.PartialResult())
                if partial.get("partial", "").strip():
                    # Only log partial results at debug level to avoid spam
                    partial_text = partial["partial"].strip()
                    if len(partial_text) > 3:  # Only log meaningful partials
                        self.logger.debug(f"🎤 Partial: {partial_text}")
                
                # Small delay to prevent CPU spinning (like official example)
                time.sleep(0.1)
                
                # Debug: Log recording status periodically
                if hasattr(self, '_last_status_log'):
                    if time.time() - self._last_status_log > 5.0:  # Every 5 seconds
                        self.logger.debug(f"🎤 ASR recording loop: is_recording={self.is_recording}, paused={self._recording_paused}")
                        self._last_status_log = time.time()
                else:
                    self._last_status_log = time.time()
                
            except Exception as e:
                self.logger.error(f"Error in recording loop: {e}")
                time.sleep(0.1)
                continue
    
    def transcribe_file(self, audio_file_path: str) -> Optional[str]:
        """Transcribe an audio file."""
        if not self.rec:
            self.logger.error("Vosk model not loaded")
            return None
        
        try:
            self.logger.info(f"🎤 Transcribing file: {audio_file_path}")
            
            # Read audio file
            import wave
            with wave.open(audio_file_path, "rb") as wf:
                # Check if audio format is compatible
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                    self.logger.warning("Audio file must be 16kHz, 16-bit, mono")
                    return None
                
                # Read all frames
                data = wf.readframes(wf.getnframes())
                
                # Process with Vosk
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    transcription = result.get("text", "").strip()
                    
                    if transcription:
                        self.logger.debug(f"🎤 File transcription: {transcription}")
                        return transcription
                    
        except Exception as e:
            self.logger.error(f"Failed to transcribe file: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the ASR worker."""
        return {
            "is_recording": self.is_recording,
            "is_paused": self.is_paused(),
            "is_processing": self.is_processing(),
            "model_loaded": self.model is not None,
            "recognizer_ready": self.rec is not None,
            "sample_rate": 16000,
            "channels": 1,
            "last_transcription": self._last_transcription
        }
    
    def get_last_transcription(self) -> Optional[str]:
        """Get the last transcription for debugging purposes."""
        return self._last_transcription
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self.stop_recording()
            
            if self.audio:
                try:
                    self.audio.terminate()
                except Exception as e:
                    self.logger.debug(f"Error terminating PyAudio: {e}")
                finally:
                    self.audio = None
            
            self.logger.info("ASR worker cleaned up")
        except Exception as e:
            self.logger.error(f"Error during ASR cleanup: {e}")


# Convenience function for creating ASR worker
def create_asr_worker() -> ASRWorker:
    """Create and return a new ASR worker instance."""
    return ASRWorker()
