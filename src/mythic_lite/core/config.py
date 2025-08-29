"""
Configuration module for Mythic-Lite chatbot system.
Centralizes all configuration settings and environment variables.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Temporarily disable dotenv to avoid dependency issues
# from dotenv import load_dotenv
# load_dotenv()


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "rich"))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))
    console_output: bool = field(default_factory=lambda: os.getenv("LOG_CONSOLE", "true").lower() == "true")


@dataclass
class LLMConfig:
    """LLM model configuration settings."""
    model_repo: str = field(default_factory=lambda: os.getenv("LLM_MODEL_REPO", "MaziyarPanahi/gemma-3-1b-it-GGUF"))
    model_filename: str = field(default_factory=lambda: os.getenv("LLM_MODEL_FILENAME", "gemma-3-1b-it.Q4_K_M.gguf"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "140")))  # Engaging with lore but still concise
    temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.85")))  # Slightly increased for more engaging responses
    context_window: int = field(default_factory=lambda: int(os.getenv("LLM_CONTEXT_WINDOW", "2048")))  # Increased from 512 for better memory
    
    def __post_init__(self):
        """Set environment variables to control llama-cpp-python output."""
        if not os.getenv("LLAMA_CPP_VERBOSE"):
            os.environ["LLAMA_CPP_VERBOSE"] = "0"
        if not os.getenv("LLAMA_CPP_LOG_LEVEL"):
            os.environ["LLAMA_CPP_LOG_LEVEL"] = "ERROR"


@dataclass
class TTSConfig:
    """Text-to-speech configuration settings."""
    voice_path: str = field(default_factory=lambda: os.getenv("TTS_VOICE_PATH", "ljspeech-high"))
    sample_rate: int = field(default_factory=lambda: int(os.getenv("TTS_SAMPLE_RATE", "22050")))
    channels: int = field(default_factory=lambda: int(os.getenv("TTS_CHANNELS", "1")))
    audio_format: str = field(default_factory=lambda: os.getenv("TTS_AUDIO_FORMAT", "paInt16"))
    enable_audio: bool = field(default_factory=lambda: os.getenv("TTS_ENABLE_AUDIO", "true").lower() == "true")
    
    # Voice quality controls
    pitch: float = field(default_factory=lambda: float(os.getenv("TTS_PITCH", "0.0")))  # -20.0 to 20.0, 0.0 is normal
    speed: float = field(default_factory=lambda: float(os.getenv("TTS_SPEED", "1.0")))  # 0.1 to 5.0, 1.0 is normal
    
    # Available Piper voices (these will be automatically mapped to correct paths)
    AVAILABLE_VOICES = {
        "amy-low": "en/en_US/amy/low",
        "ljspeech-medium": "en/en_US/ljspeech/medium",
        "ljspeech-high": "en/en_US/ljspeech/high"
    }


@dataclass
class ASRConfig:
    """Automatic Speech Recognition configuration settings."""
    model_name: str = field(default_factory=lambda: os.getenv("ASR_MODEL_NAME", "base"))
    model_size: str = field(default_factory=lambda: os.getenv("ASR_MODEL_SIZE", "tiny"))
    language: str = field(default_factory=lambda: os.getenv("ASR_LANGUAGE", "en"))
    enable_asr: bool = field(default_factory=lambda: os.getenv("ASR_ENABLE", "true").lower() == "true")
    chunk_length: float = field(default_factory=lambda: float(os.getenv("ASR_CHUNK_LENGTH", "30.0")))
    sample_rate: int = field(default_factory=lambda: int(os.getenv("ASR_SAMPLE_RATE", "16000")))
    channels: int = field(default_factory=lambda: int(os.getenv("ASR_CHANNELS", "1")))
    audio_format: str = field(default_factory=lambda: os.getenv("ASR_AUDIO_FORMAT", "paInt16"))


@dataclass
class MemoryConfig:
    """Memory configuration settings."""
    max_tokens: int = field(default_factory=lambda: int(os.getenv("MEMORY_MAX_TOKENS", "120")))  # Memory summary length
    temperature: float = field(default_factory=lambda: float(os.getenv("MEMORY_TEMPERATURE", "0.1")))  # Memory generation temperature
    cache_size: int = field(default_factory=lambda: int(os.getenv("MEMORY_CACHE_SIZE", "100")))  # Maximum cached memories
    
    def __post_init__(self):
        """Set environment variables to control llama-cpp-python output."""
        if not os.getenv("LLAMA_CPP_VERBOSE"):
            os.environ["LLAMA_CPP_VERBOSE"] = "0"
        if not os.getenv("LLAMA_CPP_LOG_LEVEL"):
            os.environ["LLAMA_CPP_LOG_LEVEL"] = "ERROR"


@dataclass
class ConversationConfig:
    """Conversation and memory configuration settings."""
    max_conversation_length: int = field(default_factory=lambda: int(os.getenv("CONVERSATION_MAX_LENGTH", "20")))  # Increased from 12 for better memory
    max_tokens_per_message: int = field(default_factory=lambda: int(os.getenv("CONVERSATION_MAX_TOKENS_PER_MESSAGE", "300")))  # Increased from 200
    memory_compression_threshold: int = field(default_factory=lambda: int(os.getenv("CONVERSATION_MEMORY_THRESHOLD", "12")))  # Increased from 8 for better retention
    auto_summarize_interval: int = field(default_factory=lambda: int(os.getenv("CONVERSATION_AUTO_SUMMARIZE", "6")))  # Increased from 4 for less aggressive summarization


@dataclass
class UIConfig:
    """User interface configuration settings."""
    enable_colors: bool = field(default_factory=lambda: os.getenv("UI_ENABLE_COLORS", "true").lower() == "true")
    enable_progress_bars: bool = field(default_factory=lambda: os.getenv("UI_ENABLE_PROGRESS", "true").lower() == "true")
    enable_animations: bool = field(default_factory=lambda: os.getenv("UI_ENABLE_ANIMATIONS", "true").lower() == "true")
    theme: str = field(default_factory=lambda: os.getenv("UI_THEME", "default"))


@dataclass
class Config:
    """Main configuration class that aggregates all configuration sections."""
    
    # Environment
    debug_mode: bool = field(default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true")
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    # Paths
    base_path: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    runtime_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "runtime")
    models_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "runtime" / "models")
    logs_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    
    # Configuration sections
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    def __post_init__(self):
        """Set environment variables to control llama-cpp-python output."""
        # Set llama-cpp-python environment variables to control output
        if not os.getenv("LLAMA_CPP_VERBOSE"):
            os.environ["LLAMA_CPP_VERBOSE"] = "0"
        if not os.getenv("LLAMA_CPP_LOG_LEVEL"):
            os.environ["LLAMA_CPP_LOG_LEVEL"] = "ERROR"
        if not os.getenv("LLAMA_CPP_SILENT"):
            os.environ["LLAMA_CPP_SILENT"] = "1"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            "debug_mode": self.debug_mode,
            "environment": self.environment,
            "base_path": str(self.base_path),
            "runtime_path": str(self.runtime_path),
            "models_path": str(self.models_path),
            "logs_path": str(self.logs_path),
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_path": self.logging.file_path,
                "console_output": self.logging.console_output
            },
            "llm": {
                "model_repo": self.llm.model_repo,
                "model_filename": self.llm.model_filename,
                "max_tokens": self.llm.max_tokens,
                "temperature": self.llm.temperature,
                "context_window": self.llm.context_window
            },
            "tts": {
                "voice_path": self.tts.voice_path,
                "sample_rate": self.tts.sample_rate,
                "channels": self.tts.channels,
                "audio_format": self.tts.audio_format,
                "enable_audio": self.tts.enable_audio,
                "pitch": self.tts.pitch,
                "speed": self.tts.speed
            },
            "asr": {
                "model_name": self.asr.model_name,
                "model_size": self.asr.model_size,
                "language": self.asr.language,
                "enable_asr": self.asr.enable_asr,
                "chunk_length": self.asr.chunk_length,
                "sample_rate": self.asr.sample_rate,
                "channels": self.asr.channels,
                "audio_format": self.asr.audio_format
            },
            "memory": {
                "max_tokens": self.memory.max_tokens,
                "temperature": self.memory.temperature,
                "cache_size": self.memory.cache_size
            },
            "conversation": {
                "max_conversation_length": self.conversation.max_conversation_length,
                "max_tokens_per_message": self.conversation.max_tokens_per_message,
                "memory_compression_threshold": self.conversation.memory_compression_threshold,
                "auto_summarize_interval": self.conversation.auto_summarize_interval
            },
            "ui": {
                "enable_colors": self.ui.enable_colors,
                "enable_progress_bars": self.ui.enable_progress_bars,
                "enable_animations": self.ui.enable_animations,
                "theme": self.ui.theme
            }
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
