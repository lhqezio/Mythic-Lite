"""
Logging system for Mythic-Lite chatbot system.

Provides a centralized logging system with consistent formatting,
file rotation, and performance monitoring.
"""

import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager

from ..core.config import get_config, LogLevel


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class PerformanceLogger:
    """Performance monitoring logger."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str, success: bool = True) -> float:
        """End timing an operation and log the result."""
        if operation not in self.start_times:
            self.logger.warning(f"Timer for '{operation}' was not started")
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        status = "SUCCESS" if success else "FAILED"
        
        self.logger.info(f"Operation '{operation}' completed in {duration:.3f}s ({status})")
        del self.start_times[operation]
        
        return duration
    
    @contextmanager
    def timer(self, operation: str):
        """Context manager for timing operations."""
        self.start_timer(operation)
        try:
            yield
            self.end_timer(operation, success=True)
        except Exception as e:
            self.end_timer(operation, success=False)
            raise


class LoggerManager:
    """Centralized logger management system."""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.performance_loggers: Dict[str, PerformanceLogger] = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self) -> None:
        """Setup the root logger with default configuration."""
        config = get_config()
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.logging.level.value))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        if config.logging.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = ColoredFormatter(config.logging.format)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Add file handler
        if config.logging.file_output and config.logging.file_path:
            self._setup_file_handler(root_logger, config)
    
    def _setup_file_handler(self, logger: logging.Logger, config: Any) -> None:
        """Setup file handler with rotation."""
        log_file = Path(config.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.logging.max_file_size,
            backupCount=config.logging.backup_count
        )
        
        # Use standard formatter for file output
        file_formatter = logging.Formatter(config.logging.format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the specified name."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
            
            # Create performance logger
            self.performance_loggers[name] = PerformanceLogger(logger)
        
        return self.loggers[name]
    
    def get_performance_logger(self, name: str) -> PerformanceLogger:
        """Get performance logger for the specified name."""
        if name not in self.performance_loggers:
            self.get_logger(name)  # This will create both loggers
        
        return self.performance_loggers[name]
    
    def set_level(self, level: LogLevel) -> None:
        """Set logging level for all loggers."""
        for logger in self.loggers.values():
            logger.setLevel(getattr(logging, level.value))
        
        # Also set root logger level
        logging.getLogger().setLevel(getattr(logging, level.value))
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Get statistics about loggers."""
        stats = {
            'total_loggers': len(self.loggers),
            'logger_names': list(self.loggers.keys()),
            'performance_loggers': len(self.performance_loggers)
        }
        
        # Add handler information
        root_logger = logging.getLogger()
        stats['root_handlers'] = len(root_logger.handlers)
        stats['root_level'] = root_logger.level
        
        return stats


# Global logger manager instance
_logger_manager: Optional[LoggerManager] = None


def get_logger_manager() -> LoggerManager:
    """Get the global logger manager instance."""
    global _logger_manager
    
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return get_logger_manager().get_logger(name)


def get_performance_logger(name: str) -> PerformanceLogger:
    """Get a performance logger with the specified name."""
    return get_logger_manager().get_performance_logger(name)


def set_log_level(level: LogLevel) -> None:
    """Set the logging level for all loggers."""
    get_logger_manager().set_level(level)


def get_logger_stats() -> Dict[str, Any]:
    """Get statistics about the logging system."""
    return get_logger_manager().get_logger_stats()


# Convenience functions for common logging patterns
def log_function_entry(logger: logging.Logger, function_name: str, **kwargs) -> None:
    """Log function entry with parameters."""
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Entering {function_name}({params})")


def log_function_exit(logger: logging.Logger, function_name: str, result: Any = None) -> None:
    """Log function exit with result."""
    if result is not None:
        logger.debug(f"Exiting {function_name} -> {result}")
    else:
        logger.debug(f"Exiting {function_name}")


def log_error_with_context(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """Log error with additional context."""
    error_msg = f"Error in {context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)


def log_performance_metric(logger: logging.Logger, operation: str, duration: float, 
                          success: bool = True, **kwargs) -> None:
    """Log performance metrics."""
    status = "SUCCESS" if success else "FAILED"
    extra_info = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    if extra_info:
        logger.info(f"Performance: {operation} completed in {duration:.3f}s ({status}) - {extra_info}")
    else:
        logger.info(f"Performance: {operation} completed in {duration:.3f}s ({status})")


# Context manager for automatic logging
@contextmanager
def logged_operation(logger: logging.Logger, operation_name: str, **kwargs):
    """Context manager for logging operations with timing."""
    perf_logger = get_performance_logger(logger.name)
    
    with perf_logger.timer(operation_name):
        try:
            log_function_entry(logger, operation_name, **kwargs)
            yield
            log_function_exit(logger, operation_name)
        except Exception as e:
            log_error_with_context(logger, e, operation_name)
            raise


# Initialize default loggers
def initialize_logging() -> None:
    """Initialize the logging system."""
    config = get_config()
    
    # Create logger manager
    manager = get_logger_manager()
    
    # Set initial log level
    manager.set_level(config.logging.level)
    
    # Log initialization
    logger = get_logger("logging-system")
    logger.info("Logging system initialized")
    logger.debug(f"Log level: {config.logging.level.value}")
    logger.debug(f"Console output: {config.logging.console_output}")
    logger.debug(f"File output: {config.logging.file_output}")


# Auto-initialize logging when module is imported
initialize_logging()
