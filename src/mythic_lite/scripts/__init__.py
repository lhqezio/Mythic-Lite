"""
Scripts for Mythic-Lite AI chatbot system.

This module contains utility scripts for:
- Manual Vosk model download
- Model initialization
- Environment setup
"""

from .download_vosk_manual import download_vosk_model
from .initialize_models import initialize_models
from .setup_environment import setup_environment

__all__ = [
    'download_vosk_model',
    'initialize_models',
    'setup_environment'
]