"""
Configuration management for Mythic-Lite chatbot system.

Provides a centralized configuration system with validation, persistence,
and environment variable support.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    console_output: bool = True
    file_output: bool = False
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class LLMConfig:
    """Language model configuration."""
    model_repo: str = "MaziyarPanahi/gemma-3-1b-it-GGUF"
    model_filename: str = "gemma-3-1b-it.Q4_K_M.gguf"
    max_tokens: int = 140
    temperature: float = 0.85
    context_window: int = 2048
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    n_gpu_layers: int = 0
    n_threads: int = 4


@dataclass
class TTSConfig:
    """Text-to-speech configuration."""
    enable_audio: bool = True
    voice_id: str = "pNInz6obpgDQGcFmaJgB"
    model_id: str = "eleven_monolingual_v1"
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True
    output_format: str = "mp3_44100_128"
    api_key: Optional[str] = None


@dataclass
class ASRConfig:
    """Automatic speech recognition configuration."""
    enable_asr: bool = False
    model_name: str = "base"
    language: str = "en"
    task: str = "transcribe"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 5
    best_of: int = 5
    patience: float = 1.0
    length_penalty: float = 1.0
    repetition_penalty: float = 1.0
    log_prob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    compression_ratio_threshold: float = 2.4
    condition_on_previous_text: bool = True
    prompt_reset_on_temperature: bool = False
    temperature: float = 0.0
    initial_prompt: Optional[str] = None
    word_timestamps: bool = False
    prepend_punctuations: str = "\"'"¿([{-"
    append_punctuations: str = "\"'.。,，!！?？:：")]}、"


@dataclass
class MemoryConfig:
    """Memory management configuration."""
    enable_memory: bool = True
    max_memories: int = 1000
    memory_ttl_hours: int = 24 * 7  # 1 week
    summary_max_length: int = 100
    max_tokens: int = 120
    temperature: float = 0.1
    cache_size: int = 100


@dataclass
class ConversationConfig:
    """Conversation management configuration."""
    max_history_length: int = 50
    system_prompt: str = "You are Mythic, a 19th century mercenary AI. Be direct, practical, and maintain your character."
    user_prefix: str = "User: "
    assistant_prefix: str = "Mythic: "
    enable_streaming: bool = True
    timeout_seconds: int = 30


@dataclass
class SystemConfig:
    """System-wide configuration."""
    debug_mode: bool = False
    data_dir: str = "data"
    models_dir: str = "models"
    logs_dir: str = "logs"
    temp_dir: str = "temp"
    max_workers: int = 4
    enable_benchmarks: bool = True
    auto_save_interval: int = 300  # 5 minutes


@dataclass
class Config:
    """Main configuration class containing all subsystem configurations."""
    
    # Subsystem configurations
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    
    # Configuration file path
    config_file: Optional[Path] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
        self._load_environment_variables()
    
    def _validate_config(self):
        """Validate configuration parameters."""
        # LLM validation
        if self.llm.max_tokens <= 0:
            raise ValueError("LLM max_tokens must be positive")
        if not 0.0 <= self.llm.temperature <= 2.0:
            raise ValueError("LLM temperature must be between 0.0 and 2.0")
        if self.llm.context_window <= 0:
            raise ValueError("LLM context_window must be positive")
        
        # TTS validation
        if not 0.0 <= self.tts.stability <= 1.0:
            raise ValueError("TTS stability must be between 0.0 and 1.0")
        if not 0.0 <= self.tts.similarity_boost <= 1.0:
            raise ValueError("TTS similarity_boost must be between 0.0 and 1.0")
        
        # Memory validation
        if self.memory.max_memories <= 0:
            raise ValueError("Memory max_memories must be positive")
        if self.memory.memory_ttl_hours <= 0:
            raise ValueError("Memory TTL must be positive")
        
        # System validation
        if self.system.max_workers <= 0:
            raise ValueError("System max_workers must be positive")
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        # TTS API key
        if not self.tts.api_key:
            self.tts.api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Debug mode
        if os.getenv("MYTHIC_DEBUG"):
            self.system.debug_mode = True
            self.logging.level = LogLevel.DEBUG
        
        # Data directory
        if os.getenv("MYTHIC_DATA_DIR"):
            self.system.data_dir = os.getenv("MYTHIC_DATA_DIR")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = asdict(self)
        
        # Convert enums to strings
        config_dict["logging"]["level"] = self.logging.level.value
        
        # Remove config_file from serialization
        config_dict.pop("config_file", None)
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        # Convert string back to enum
        if "logging" in config_dict and "level" in config_dict["logging"]:
            config_dict["logging"]["level"] = LogLevel(config_dict["logging"]["level"])
        
        return cls(**config_dict)
    
    def save(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """Save configuration to file."""
        if file_path is None:
            file_path = self.config_file or Path("config.json")
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        self.config_file = file_path
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> "Config":
        """Load configuration from file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        
        config = cls.from_dict(config_dict)
        config.config_file = file_path
        return config
    
    def get_worker_config(self, worker_name: str) -> Dict[str, Any]:
        """Get configuration for a specific worker."""
        worker_configs = {
            "llm": asdict(self.llm),
            "tts": asdict(self.tts),
            "asr": asdict(self.asr),
            "memory": asdict(self.memory),
            "conversation": asdict(self.conversation),
            "system": asdict(self.system)
        }
        
        return worker_configs.get(worker_name, {})
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        for key, value in updates.items():
            if hasattr(self, key):
                if isinstance(value, dict) and hasattr(getattr(self, key), '__dict__'):
                    # Update nested config object
                    current = getattr(self, key)
                    for sub_key, sub_value in value.items():
                        if hasattr(current, sub_key):
                            setattr(current, sub_key, sub_value)
                else:
                    setattr(self, key, value)
        
        self._validate_config()


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = _create_default_config()
    
    return _config_instance


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config_instance
    _config_instance = config


def _create_default_config() -> Config:
    """Create a default configuration instance."""
    return Config()


def load_config_from_file(file_path: Union[str, Path]) -> Config:
    """Load configuration from file and set as global instance."""
    config = Config.load(file_path)
    set_config(config)
    return config


def save_config_to_file(config: Config, file_path: Union[str, Path]) -> None:
    """Save configuration to file."""
    config.save(file_path)


def reset_config() -> None:
    """Reset the global configuration to defaults."""
    global _config_instance
    _config_instance = None
