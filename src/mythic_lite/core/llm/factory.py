"""
LLM Factory for Mythic-Lite chatbot system.

Provides a clean interface for creating different types of language models,
enabling easy swapping and configuration management.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from .base import BaseLLM, LLMConfig, ModelType
from .llama_cpp import LlamaCPPModel
from ...utils.logger import get_logger


class LLMFactory:
    """Factory for creating language model instances."""
    
    def __init__(self):
        self.logger = get_logger("llm-factory")
        self._available_models = self._discover_available_models()
    
    def _discover_available_models(self) -> Dict[str, bool]:
        """Discover which model types are available."""
        models = {}
        
        # Check LLaMA CPP availability
        try:
            import llama_cpp
            models['llama_cpp'] = True
        except ImportError:
            models['llama_cpp'] = False
        
        # Check OpenAI availability
        try:
            import openai
            models['openai'] = True
        except ImportError:
            models['openai'] = False
        
        # Check Anthropic availability
        try:
            import anthropic
            models['anthropic'] = True
        except ImportError:
            models['anthropic'] = False
        
        return models
    
    def create_model(self, config: LLMConfig) -> BaseLLM:
        """Create a language model instance based on configuration."""
        try:
            if config.model_type == ModelType.LLAMA_CPP:
                if not self._available_models.get('llama_cpp', False):
                    raise ImportError("LLaMA CPP is not available")
                return LlamaCPPModel(config)
            
            elif config.model_type == ModelType.OPENAI:
                if not self._available_models.get('openai', False):
                    raise ImportError("OpenAI is not available")
                # TODO: Implement OpenAI model
                raise NotImplementedError("OpenAI models not yet implemented")
            
            elif config.model_type == ModelType.ANTHROPIC:
                if not self._available_models.get('anthropic', False):
                    raise ImportError("Anthropic is not available")
                # TODO: Implement Anthropic model
                raise NotImplementedError("Anthropic models not yet implemented")
            
            elif config.model_type == ModelType.CUSTOM:
                # TODO: Implement custom model interface
                raise NotImplementedError("Custom models not yet implemented")
            
            else:
                raise ValueError(f"Unknown model type: {config.model_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to create model: {e}")
            raise
    
    def create_llama_cpp_model(
        self,
        model_path: Optional[str] = None,
        model_repo: Optional[str] = None,
        model_filename: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """Create a LLaMA CPP model with the given configuration."""
        config = LLMConfig(
            model_type=ModelType.LLAMA_CPP,
            model_path=model_path,
            model_repo=model_repo,
            model_filename=model_filename,
            **kwargs
        )
        
        return self.create_model(config)
    
    def create_model_from_dict(self, config_dict: Dict[str, Any]) -> BaseLLM:
        """Create a model from a dictionary configuration."""
        try:
            # Extract model type
            model_type_str = config_dict.get('model_type', 'llama_cpp')
            model_type = ModelType(model_type_str)
            
            # Create config object
            config = LLMConfig(
                model_type=model_type,
                **config_dict
            )
            
            return self.create_model(config)
            
        except Exception as e:
            self.logger.error(f"Failed to create model from dict: {e}")
            raise
    
    def create_model_from_file(self, config_file: str) -> BaseLLM:
        """Create a model from a configuration file."""
        try:
            import json
            
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            
            return self.create_model_from_dict(config_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to create model from file: {e}")
            raise
    
    def get_available_model_types(self) -> Dict[str, bool]:
        """Get information about available model types."""
        return self._available_models.copy()
    
    def validate_model_config(self, config: LLMConfig) -> Dict[str, Any]:
        """Validate a model configuration."""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'model_type': config.model_type.value,
            'available': self._available_models.get(config.model_type.value, False)
        }
        
        # Check if model type is available
        if not validation['available']:
            validation['errors'].append(f"{config.model_type.value} is not available")
            validation['valid'] = False
        
        # Validate model-specific requirements
        if config.model_type == ModelType.LLAMA_CPP:
            if not config.model_path and not config.model_repo:
                validation['errors'].append("LLaMA CPP requires model_path or model_repo")
                validation['valid'] = False
            
            if config.model_path and not Path(config.model_path).exists():
                validation['warnings'].append(f"Model path does not exist: {config.model_path}")
        
        # Validate general parameters
        if config.max_tokens <= 0:
            validation['errors'].append("Max tokens must be positive")
            validation['valid'] = False
        
        if config.temperature < 0.0 or config.temperature > 2.0:
            validation['warnings'].append("Temperature should be between 0.0 and 2.0")
        
        if config.context_window <= 0:
            validation['errors'].append("Context window must be positive")
            validation['valid'] = False
        
        return validation
    
    def get_default_config(self, model_type: ModelType = ModelType.LLAMA_CPP) -> LLMConfig:
        """Get a default configuration for the specified model type."""
        if model_type == ModelType.LLAMA_CPP:
            return LLMConfig(
                model_type=ModelType.LLAMA_CPP,
                model_repo="MaziyarPanahi/gemma-3-1b-it-GGUF",
                model_filename="gemma-3-1b-it.Q4_K_M.gguf",
                max_tokens=140,
                temperature=0.85,
                context_window=2048,
                n_gpu_layers=0,
                n_threads=4,
                verbose=False
            )
        
        elif model_type == ModelType.OPENAI:
            return LLMConfig(
                model_type=ModelType.OPENAI,
                max_tokens=140,
                temperature=0.85,
                context_window=4096
            )
        
        elif model_type == ModelType.ANTHROPIC:
            return LLMConfig(
                model_type=ModelType.ANTHROPIC,
                max_tokens=140,
                temperature=0.85,
                context_window=4096
            )
        
        else:
            raise ValueError(f"No default config for model type: {model_type}")


def get_llm_factory() -> LLMFactory:
    """Get a language model factory instance."""
    return LLMFactory()