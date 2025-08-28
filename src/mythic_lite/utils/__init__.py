"""
Utility components for Mythic-Lite AI chatbot system.

This module contains utility functions and classes for:
- CLI interface
- Logging
- Platform-specific input handling
"""

from .logger import Logger
from .windows_input import WindowsInput

# Use lazy import to avoid circular dependencies
def get_cli():
    """Get the CLI class (lazy import to avoid circular dependencies)."""
    from .cli import cli
    return cli

__all__ = [
    'Logger',
    'WindowsInput',
    'get_cli'
]