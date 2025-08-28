"""
Advanced logging module for Mythic-Lite chatbot system.
Provides structured logging with rich console output and file logging capabilities.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Use lazy imports to avoid circular dependencies
def get_rich_modules():
    """Get rich modules when needed."""
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.theme import Theme
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import print as rprint
    return Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint


class MythicLogger:
    """Advanced logger class with rich console output and structured logging."""
    
    def __init__(self, name: str = "mythic", config: Optional[Any] = None):
        self.name = name
        self.config = config
        self.console = None
        self.logger = None
        self.progress = None
        
        self._setup_console()
        self._setup_logging()
    
    def _setup_console(self):
        """Setup rich console with custom theme."""
        try:
            # Get rich modules when needed
            Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint = get_rich_modules()
            
            # Custom theme for Mythic
            mythic_theme = Theme({
                "info": "cyan",
                "warning": "yellow",
                "error": "red",
                "critical": "red bold",
                "success": "green",
                "mythic": "magenta bold",
                "user": "blue",
                "system": "dim white",
                "debug": "dim cyan"
            })
            
            self.console = Console(theme=mythic_theme, width=100)
            
            # Disable colors if configured
            if self.config and hasattr(self.config, 'ui') and hasattr(self.config.ui, 'enable_colors'):
                if not self.config.ui.enable_colors:
                    self.console.no_color = True
                    
        except ImportError:
            # Fallback to basic console if rich is not available
            self.console = None
    
    def _setup_logging(self):
        """Setup logging with rich handlers."""
        # Create logger
        self.logger = logging.getLogger(self.name)
        
        # Set log level based on config or default to INFO
        if self.config and hasattr(self.config, 'logging') and hasattr(self.config.logging, 'level'):
            self.logger.setLevel(getattr(logging, self.config.logging.level.upper()))
        else:
            self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Only setup rich handler if available, otherwise use basic console handler
        if self.console:
            try:
                Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint = get_rich_modules()
                
                rich_handler = RichHandler(
                    console=self.console,
                    show_time=True,
                    show_path=False,
                    markup=True,
                    rich_tracebacks=True
                )
                rich_handler.setLevel(self.logger.level)  # Use same level as logger
                
                # Create formatter for rich handler
                rich_formatter = logging.Formatter(
                    '%(message)s'
                )
                rich_handler.setFormatter(rich_formatter)
                self.logger.addHandler(rich_handler)
                
            except Exception:
                # Fallback to basic console handler if rich setup fails
                self._setup_basic_handler()
        else:
            # Use basic console handler if rich is not available
            self._setup_basic_handler()
    
    def _setup_basic_handler(self):
        """Setup basic console handler for logging."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.logger.level)  # Use same level as logger
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message)
    
    def success(self, message: str, **kwargs):
        """Log success message with custom styling."""
        if self.console:
            try:
                self.console.print(f"✅ {message}", style="bold green", **kwargs)
            except:
                self.logger.info(f"✅ {message}")
        else:
            self.logger.info(f"✅ {message}")
    
    def mythic_speak(self, message: str, **kwargs):
        """Log Mythic's speech with special styling."""
        if self.console:
            try:
                self.console.print(f"Mythic: {message}", style="bold magenta", **kwargs)
            except:
                self.logger.info(f"Mythic: {message}")
        else:
            self.logger.info(f"Mythic: {message}")
    
    def user_speak(self, message: str, **kwargs):
        """Log user's speech with special styling."""
        if self.console:
            try:
                self.console.print(f"You: {message}", style="bold blue", **kwargs)
            except:
                self.logger.info(f"You: {message}")
        else:
            self.logger.info(f"You: {message}")
    
    def system_info(self, message: str, **kwargs):
        """Log system information with special styling."""
        if self.console:
            try:
                self.console.print(f"ℹ {message}", style="bold cyan", **kwargs)
            except:
                self.logger.info(f"ℹ {message}")
        else:
            self.logger.info(f"ℹ {message}")
    
    def print_panel(self, content: str, title: str = "", style: str = "blue"):
        """Print content in a rich panel."""
        if self.console:
            try:
                Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint = get_rich_modules()
                self.console.print(Panel(content, title=title, style=style))
            except:
                print(f"=== {title} ===")
                print(content)
                print("=" * (len(title) + 8))
        else:
            print(f"=== {title} ===")
            print(content)
            print("=" * (len(title) + 8))
    
    def print_table(self, data: Dict[str, Any], title: str = ""):
        """Print data in a rich table."""
        if self.console:
            try:
                Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint = get_rich_modules()
                table = Table(title=title, show_header=True, header_style="bold magenta")
                
                for key, value in data.items():
                    table.add_column(key, style="cyan")
                    table.add_column(str(value), style="white")
                
                self.console.print(table)
            except:
                self._print_simple_table(data, title)
        else:
            self._print_simple_table(data, title)
    
    def _print_simple_table(self, data: Dict[str, Any], title: str = ""):
        """Print data in a simple table format."""
        if title:
            print(f"\n{title}")
            print("-" * len(title))
        
        for key, value in data.items():
            print(f"{key}: {value}")
    
    def start_progress(self, description: str = "Processing..."):
        """Start a progress indicator."""
        # Disabled to avoid Task-related issues
        return None
    
    def update_progress(self, description: str = None):
        """Update progress description."""
        # Disabled to avoid Task-related issues
        pass
    
    def stop_progress(self):
        """Stop the progress indicator."""
        # Disabled to avoid Task-related issues
        pass
    
    def show_speech_status(self, status: str, end: str = "\n"):
        """Show speech status with appropriate emoji and styling."""
        if self.console:
            try:
                # Clear any existing status first
                self.clear_line()
                
                if status == "listening":
                    self.console.print("🎤 Listening...", style="bold cyan", end=end)
                elif status == "thinking":
                    self.console.print("🤔 Thinking...", style="blue", end=end)
                elif status == "processing":
                    self.console.print("🔄 Processing...", style="yellow", end=end)
                elif status == "complete":
                    self.console.print("✅ Complete", style="green", end=end)
                elif status == "error":
                    self.console.print("❌ Error", style="red", end=end)
                else:
                    self.console.print(f"🎤 {status}", end=end)
            except:
                print(f"🎤 {status}", end=end)
        else:
            print(f"🎤 {status}", end=end)
    
    def clear_line(self):
        """Clear the current line for clean updates."""
        if self.console:
            try:
                # Use carriage return to go back to start of line
                self.console.print("\r", end="")
                # Clear the entire line with spaces
                self.console.print(" " * 100, end="\r")
            except:
                pass
    
    def update_speech_status(self, status: str):
        """Update speech status without newline - for real-time updates."""
        if self.console:
            try:
                # Clear current line and show new status
                self.clear_line()
                self.show_speech_status(status, end="")
                # Force flush to ensure immediate display
                self.console.file.flush()
            except:
                pass
    
    def print_banner(self):
        """Print the Mythic banner."""
        if self.console:
            try:
                Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint = get_rich_modules()
                banner = """
 ╔══════════════════════════════════════════════════════════════╗
 ║                    MYTHIC - 19th Century Mercenary          ║
 ║                                                              ║
 ║  A fierce female warrior from the Victorian era stands      ║
 ║  before you, ready for adventure and conversation.          ║
 ╚══════════════════════════════════════════════════════════════╝
                """
                self.console.print(Panel(banner, style="bold magenta"))
            except:
                self._print_simple_banner()
        else:
            self._print_simple_banner()
    
    def _print_simple_banner(self):
        """Print a simple banner without rich formatting."""
        print("""
 ╔══════════════════════════════════════════════════════════════╗
 ║                    MYTHIC - 19th Century Mercenary          ║
 ║                                                              ║
 ║  A fierce female warrior from the Victorian era stands      ║
 ║  before you, ready for adventure and conversation.          ║
 ╚══════════════════════════════════════════════════════════════╝
        """)
    
    def print_help(self):
        """Print help information."""
        if self.console:
            try:
                Console, RichHandler, Theme, Panel, Text, Progress, SpinnerColumn, TextColumn, Table, rprint = get_rich_modules()
                help_text = """
Available Commands:
• debug - Access troubleshooting and debug options
• status - Show system and model status
• quit or exit - Exit the chatbot
• help - Show this help message

Special Features:
• Automatic text-to-speech with streaming
• Intelligent memory management
• Context-aware conversations
• Victorian-era personality
                """
                self.console.print(Panel(help_text, title="Help", style="blue"))
            except:
                self._print_simple_help()
        else:
            self._print_simple_help()
    
    def _print_simple_help(self):
        """Print simple help without rich formatting."""
        print("""
Available Commands:
• debug - Access troubleshooting and debug options
• status - Show system and model status
• quit or exit - Exit the chatbot
• help - Show this help message

Special Features:
• Automatic text-to-speech with streaming
• Intelligent memory management
• Context-aware conversations
• Victorian-era personality
        """)
    
    def log_configuration(self):
        """Log the current configuration."""
        if self.config and hasattr(self.config, 'to_dict'):
            try:
                config_dict = self.config.to_dict()
                self.info("Configuration loaded")
                
                if self.config.debug_mode:
                    self.print_table(config_dict, "Current Configuration")
            except:
                self.info("Configuration loaded (could not display details)")
        else:
            self.info("Configuration loaded (no config object)")
    
    def log_error_with_context(self, error: Exception, context: str = "", **kwargs):
        """Log error with additional context."""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            **kwargs
        }
        self.error(f"Error occurred: {error}")
        
        if self.config and hasattr(self.config, 'debug_mode') and self.config.debug_mode:
            if self.console:
                try:
                    self.console.print_exception()
                except:
                    pass


# Global logger instance and debug mode
_logger = None
_global_debug_config = None

def get_logger(name: str = "mythic") -> MythicLogger:
    """Get or create a logger instance."""
    global _logger, _global_debug_config
    if _logger is None:
        _logger = MythicLogger(name, _global_debug_config)
    return _logger


def setup_logging(name: str = "mythic", config: Optional[Any] = None) -> MythicLogger:
    """Setup and return a logger instance."""
    global _logger, _global_debug_config
    _global_debug_config = config  # Store globally for other loggers
    _logger = MythicLogger(name, config)
    return _logger


# Convenience functions for quick logging
def log_info(message: str, **kwargs):
    """Quick info logging."""
    get_logger().info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Quick warning logging."""
    get_logger().warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Quick error logging."""
    get_logger().error(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Quick debug logging."""
    get_logger().debug(message, **kwargs)


# Backward compatibility
Logger = MythicLogger
