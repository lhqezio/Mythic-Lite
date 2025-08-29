"""
Configuration Manager for Mythic-Lite chatbot system.

Provides a clean interface for managing system configuration,
including loading, saving, and validating settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict

from ..core.config import get_config, Config
from .logger import get_logger


class ConfigManager:
    """Manages system configuration and settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger("config-manager")
        self.config_path = config_path or self._get_default_config_path()
        self.config = get_config()
        
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".mythic-lite"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")
    
    def load_config(self) -> Config:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update config with loaded data
                self._update_config_from_dict(config_data)
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.info("No configuration file found, using defaults")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            
        return self.config
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            # Convert config to dictionary
            config_dict = asdict(self.config)
            
            # Ensure config directory exists
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary data."""
        try:
            # Update logging config
            if 'logging' in config_data:
                for key, value in config_data['logging'].items():
                    if hasattr(self.config.logging, key):
                        setattr(self.config.logging, key, value)
            
            # Update LLM config
            if 'llm' in config_data:
                for key, value in config_data['llm'].items():
                    if hasattr(self.config.llm, key):
                        setattr(self.config.llm, key, value)
            
            # Update TTS config
            if 'tts' in config_data:
                for key, value in config_data['tts'].items():
                    if hasattr(self.config.tts, key):
                        setattr(self.config.tts, key, value)
            
            # Update ASR config
            if 'asr' in config_data:
                for key, value in config_data['asr'].items():
                    if hasattr(self.config.asr, key):
                        setattr(self.config.asr, key, value)
            
            # Update memory config
            if 'memory' in config_data:
                for key, value in config_data['memory'].items():
                    if hasattr(self.config.memory, key):
                        setattr(self.config.memory, key, value)
            
            # Update conversation config
            if 'conversation' in config_data:
                for key, value in config_data['conversation'].items():
                    if hasattr(self.config.conversation, key):
                        setattr(self.config.conversation, key, value)
            
            # Update system config
            if 'system' in config_data:
                for key, value in config_data['system'].items():
                    if hasattr(self.config.system, key):
                        setattr(self.config.system, key, value)
                        
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
    
    def get_config_value(self, section: str, key: str) -> Any:
        """Get a specific configuration value."""
        try:
            section_obj = getattr(self.config, section, None)
            if section_obj:
                return getattr(section_obj, key, None)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get config value {section}.{key}: {e}")
            return None
    
    def set_config_value(self, section: str, key: str, value: Any) -> bool:
        """Set a specific configuration value."""
        try:
            section_obj = getattr(self.config, section, None)
            if section_obj and hasattr(section_obj, key):
                setattr(section_obj, key, value)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to set config value {section}.{key}: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate LLM config
            if not self.config.llm.model_repo:
                validation_results['errors'].append("LLM model repository not specified")
                validation_results['valid'] = False
            
            if self.config.llm.max_tokens <= 0:
                validation_results['errors'].append("LLM max tokens must be positive")
                validation_results['valid'] = False
            
            # Validate TTS config
            if not self.config.tts.voice_path:
                validation_results['warnings'].append("TTS voice path not specified")
            
            # Validate ASR config
            if self.config.asr.enable_asr and not self.config.asr.model_name:
                validation_results['warnings'].append("ASR enabled but model name not specified")
            
            # Validate memory config
            if self.config.memory.cache_size <= 0:
                validation_results['errors'].append("Memory cache size must be positive")
                validation_results['valid'] = False
            
        except Exception as e:
            validation_results['errors'].append(f"Configuration validation failed: {e}")
            validation_results['valid'] = False
        
        return validation_results
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            # Create new default config
            self.config = get_config()
            
            # Save default config
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to a file."""
        try:
            config_dict = asdict(self.config)
            
            with open(export_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            self.logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(import_path, 'r') as f:
                config_data = json.load(f)
            
            # Update config with imported data
            self._update_config_from_dict(config_data)
            
            # Save imported config
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        try:
            return {
                'logging': {
                    'level': self.config.logging.level,
                    'format': self.config.logging.format
                },
                'llm': {
                    'model_repo': self.config.llm.model_repo,
                    'max_tokens': self.config.llm.max_tokens,
                    'temperature': self.config.llm.temperature
                },
                'tts': {
                    'voice_path': self.config.tts.voice_path,
                    'sample_rate': self.config.tts.sample_rate,
                    'enabled': self.config.tts.enable_audio
                },
                'asr': {
                    'model_name': self.config.asr.model_name,
                    'enabled': self.config.asr.enable_asr
                },
                'memory': {
                    'cache_size': self.config.memory.cache_size,
                    'max_tokens': self.config.memory.max_tokens
                },
                'conversation': {
                    'max_length': self.config.conversation.max_conversation_length,
                    'auto_summarize': self.config.conversation.auto_summarize_interval
                },
                'system': {
                    'debug_mode': self.config.system.debug_mode,
                    'base_path': str(self.config.system.base_path)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get config summary: {e}")
            return {}


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get a configuration manager instance."""
    return ConfigManager(config_path)