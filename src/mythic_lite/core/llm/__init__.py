"""
LLM abstraction module for Mythic-Lite chatbot system.

This module provides a clean interface for different language models,
allowing easy swapping of LLaMA CPP models or similar alternatives.
"""

from .base import BaseLLM, LLMResponse, LLMConfig
from .llama_cpp import LlamaCPPModel
from .factory import LLMFactory

__all__ = [
    'BaseLLM',
    'LLMResponse', 
    'LLMConfig',
    'LlamaCPPModel',
    'LLMFactory'
]