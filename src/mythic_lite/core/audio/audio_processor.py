"""
Audio Processor for Mythic-Lite chatbot system.

This module provides audio processing utilities for manipulating
audio data, including format conversion and audio enhancement.
"""

import numpy as np
from typing import Optional, Union, Tuple
from pathlib import Path

# Make scipy import optional for testing
try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class AudioProcessor:
    """Audio processing utilities for audio manipulation."""
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'ogg', 'flac']
    
    def convert_audio_format(self, audio_data: bytes, 
                           input_format: str, 
                           output_format: str,
                           sample_rate: int = 22050,
                           channels: int = 1) -> Optional[bytes]:
        """Convert audio data between different formats."""
        try:
            if input_format == output_format:
                return audio_data
            
            # This is a placeholder - actual format conversion would need
            # additional libraries like pydub or soundfile
            self.logger.warning(f"Format conversion from {input_format} to {output_format} not implemented")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Failed to convert audio format: {e}")
            return None
    
    def resample_audio(self, audio_data: bytes, 
                      original_rate: int, 
                      target_rate: int,
                      channels: int = 1) -> Optional[bytes]:
        """Resample audio data to a different sample rate."""
        try:
            if not SCIPY_AVAILABLE:
                self.logger.warning("Scipy not available - resampling disabled")
                return audio_data
            
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Reshape if stereo
            if channels == 2:
                audio_array = audio_array.reshape(-1, 2)
            
            # Resample using scipy
            resampled = signal.resample(audio_array, 
                                      int(len(audio_array) * target_rate / original_rate))
            
            # Convert back to bytes
            return resampled.astype(np.int16).tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to resample audio: {e}")
            return None
    
    def normalize_audio(self, audio_data: bytes, 
                       target_db: float = -20.0) -> Optional[bytes]:
        """Normalize audio to a target dB level."""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate RMS
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            
            if rms == 0:
                return audio_data
            
            # Calculate target RMS
            target_rms = 10 ** (target_db / 20.0) * 32767
            
            # Apply gain
            gain = target_rms / rms
            normalized = audio_array * gain
            
            # Clip to prevent overflow
            normalized = np.clip(normalized, -32768, 32767)
            
            return normalized.astype(np.int16).tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to normalize audio: {e}")
            return None
    
    def apply_noise_reduction(self, audio_data: bytes, 
                            sample_rate: int = 22050) -> Optional[bytes]:
        """Apply basic noise reduction to audio data."""
        try:
            if not SCIPY_AVAILABLE:
                self.logger.warning("Scipy not available - noise reduction disabled")
                return audio_data
            
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Simple high-pass filter to remove low-frequency noise
            nyquist = sample_rate / 2
            cutoff = 80  # Hz
            normalized_cutoff = cutoff / nyquist
            
            # Design filter
            b, a = signal.butter(4, normalized_cutoff, btype='high')
            
            # Apply filter
            filtered = signal.filtfilt(b, a, audio_array)
            
            return filtered.astype(np.int16).tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to apply noise reduction: {e}")
            return None
    
    def get_audio_info(self, audio_data: bytes, 
                      sample_rate: int = 22050,
                      channels: int = 1) -> dict:
        """Get information about audio data."""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            duration = len(audio_array) / (sample_rate * channels)
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            peak = np.max(np.abs(audio_array))
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'samples': len(audio_array),
                'rms': rms,
                'peak': peak,
                'size_bytes': len(audio_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get audio info: {e}")
            return {}
    
    def trim_silence(self, audio_data: bytes, 
                    threshold: float = 0.01,
                    sample_rate: int = 22050) -> Optional[bytes]:
        """Trim silence from the beginning and end of audio."""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Normalize to 0-1 range
            normalized = audio_array.astype(np.float32) / 32768
            
            # Find non-silent regions
            non_silent = np.abs(normalized) > threshold
            
            # Find start and end indices
            start_idx = np.argmax(non_silent)
            end_idx = len(non_silent) - np.argmax(non_silent[::-1])
            
            # Extract non-silent portion
            trimmed = audio_array[start_idx:end_idx]
            
            return trimmed.astype(np.int16).tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to trim silence: {e}")
            return None