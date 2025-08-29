"""
LLM Factory for Mythic-Lite chatbot system.

Provides a clean interface for creating different types of language models,
enabling easy swapping and configuration management.
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BaseLLM, LLMConfig, ModelType
from .llama_cpp import LlamaCPPModel
from ...utils.logger import get_logger


class LLMFactory:
    """Factory for creating language model instances with automatic discovery."""
    
    def __init__(self):
        """Initialize the LLM factory with model discovery."""
        self.logger = get_logger("llm-factory")
        self._available_models = self._discover_available_models()
        self._model_registry = self._build_model_registry()
    
    def _discover_available_models(self) -> Dict[str, bool]:
        """Discover which model types are available in the environment."""
        models = {}
        
        # Check LLaMA CPP availability
        try:
            import llama_cpp
            models['llama_cpp'] = True
            self.logger.debug("LLaMA CPP is available")
        except ImportError:
            models['llama_cpp'] = False
            self.logger.debug("LLaMA CPP is not available")
        
        # Check OpenAI availability
        try:
            import openai
            models['openai'] = True
            self.logger.debug("OpenAI is available")
        except ImportError:
            models['openai'] = False
            self.logger.debug("OpenAI is not available")
        
        # Check Anthropic availability
        try:
            import anthropic
            models['anthropic'] = True
            self.logger.debug("Anthropic is available")
        except ImportError:
            models['anthropic'] = False
            self.logger.debug("Anthropic is not available")
        
        return models
    
    def _build_model_registry(self) -> Dict[ModelType, type]:
        """Build registry of available model implementations."""
        registry = {}
        
        if self._available_models.get('llama_cpp', False):
            registry[ModelType.LLAMA_CPP] = LlamaCPPModel
        
        # TODO: Add other model implementations
        # if self._available_models.get('openai', False):
        #     registry[ModelType.OPENAI] = OpenAIModel
        # 
        # if self._available_models.get('anthropic', False):
        #     registry[ModelType.ANTHROPIC] = AnthropicModel
        
        return registry
    
    def create_model(self, config: LLMConfig) -> BaseLLM:
        """Create a language model instance based on configuration."""
        try:
            # Check if model type is supported
            if config.model_type not in self._model_registry:
                available_types = [t.value for t in self._model_registry.keys()]
                raise ValueError(f"Model type '{config.model_type.value}' not supported. Available: {available_types}")
            
            # Get model class
            model_class = self._model_registry[config.model_type]
            
            # Create and return model instance
            model = model_class(config)
            self.logger.info(f"Created {config.model_type.value} model: {model.model_name}")
            
            return model
            
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
    
    def get_supported_model_types(self) -> List[ModelType]:
        """Get list of supported model types."""
        return list(self._model_registry.keys())
    
    def validate_model_config(self, config: LLMConfig) -> Dict[str, Any]:
        """Validate a model configuration."""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'model_type': config.model_type.value,
            'available': self._available_models.get(config.model_type.value, False),
            'supported': config.model_type in self._model_registry
        }
        
        # Check if model type is available
        if not validation['available']:
            validation['errors'].append(f"{config.model_type.value} is not available")
            validation['valid'] = False
        
        # Check if model type is supported
        if not validation['supported']:
            validation['errors'].append(f"{config.model_type.value} is not supported")
            validation['valid'] = False
        
        # Validate model-specific requirements
        if config.model_type == ModelType.LLAMA_CPP:
            if not config.model_path and not config.model_repo:
                validation['errors'].append("LLaMA CPP requires model_path or model_repo")
                validation['valid'] = False
            
            if config.model_path and not Path(config.model_path).exists():
                validation['warnings'].append(f"Model path does not exist: {config.model_path}")
        
        # Validate general parameters using config validation
        try:
            config._validate_config()
        except ValueError as e:
            validation['errors'].append(str(e))
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
    
    def list_available_models(self) -> Dict[str, Any]:
        """List all available models and their status."""
        models_info = {}
        
        for model_type in ModelType:
            model_info = {
                'available': self._available_models.get(model_type.value, False),
                'supported': model_type in self._model_registry,
                'default_config': None
            }
            
            if model_type in self._model_registry:
                try:
                    model_info['default_config'] = self.get_default_config(model_type)
                except Exception as e:
                    model_info['error'] = str(e)
            
            models_info[model_type.value] = model_info
        
        return models_info
    
    def test_model_creation(self, model_type: ModelType) -> Dict[str, Any]:
        """Test if a model type can be created successfully."""
        try:
            # Get default config
            config = self.get_default_config(model_type)
            
            # Try to create model
            model = self.create_model(config)
            
            return {
                'success': True,
                'model_name': model.model_name,
                'config': config.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_type': model_type.value
            }


# Global factory instance
_factory_instance: Optional[LLMFactory] = None


def get_llm_factory() -> LLMFactory:
    """Get the global LLM factory instance."""
    global _factory_instance
    
    if _factory_instance is None:
        _factory_instance = LLMFactory()
    
    return _factory_instance


def create_model(config: LLMConfig) -> BaseLLM:
    """Create a model using the global factory."""
    return get_llm_factory().create_model(config)


def create_llama_cpp_model(**kwargs) -> BaseLLM:
    """Create a LLaMA CPP model using the global factory."""
    return get_llm_factory().create_llama_cpp_model(**kwargs)


def validate_config(config: LLMConfig) -> Dict[str, Any]:
    """Validate a model configuration using the global factory."""
    return get_llm_factory().validate_model_config(config)


def get_available_models() -> Dict[str, Any]:
    """Get available models using the global factory."""
    return get_llm_factory().list_available_models()