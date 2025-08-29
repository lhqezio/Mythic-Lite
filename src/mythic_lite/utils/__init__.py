"""
Utilities module for Mythic-Lite chatbot system.

Provides common utilities, logging, CLI, and configuration management.
"""

from .logger import (
    get_logger,
    get_performance_logger,
    set_log_level,
    get_logger_stats,
    log_function_entry,
    log_function_exit,
    log_error_with_context,
    log_performance_metric,
    logged_operation
)

from .cli import main
from .cli_commands import *
from .cli_helpers import *
from .config_manager import *
from .common import *
from .windows_input import *

__all__ = [
    # Logging
    'get_logger',
    'get_performance_logger',
    'set_log_level',
    'get_logger_stats',
    'log_function_entry',
    'log_function_exit',
    'log_error_with_context',
    'log_performance_metric',
    'logged_operation',
    
    # CLI
    'main',
    
    # Other utilities
    'safe_input',
    'safe_choice'
]