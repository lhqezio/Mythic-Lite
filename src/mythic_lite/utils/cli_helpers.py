"""
CLI helper functions for Mythic-Lite chatbot system.
Provides utility functions for CLI operations and display.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.box import ROUNDED
from typing import Optional, Any

from .logger import setup_logging, get_logger

# Rich console for beautiful output
console = Console()


def print_banner():
    """Print the Mythic-Lite banner."""
    banner_text = Text()
    banner_text.append("MYTHIC-LITE", style="magenta bold")
    banner_text.append("\n", style="white")
    banner_text.append("19th Century Mercenary AI Chatbot", style="cyan italic")
    
    banner_panel = Panel(
        banner_text,
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(banner_panel)


def print_help_table():
    """Print a help table."""
    table = Table(
        title="Available Commands",
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        border_style="cyan"
    )
    table.add_column("Command", style="cyan bold", width=15)
    table.add_column("Description", style="white")
    table.add_column("Usage", style="dim white")
    
    commands = [
        ("chat", "Start text-based chat", "mythic chat"),
        ("voice", "Start voice conversation", "mythic voice"),
        ("status", "Show system status", "mythic status"),
        ("benchmark", "Run comprehensive benchmark", "mythic benchmark"),
        ("init", "Initialize system", "mythic init"),
        ("config", "Show configuration", "mythic config"),
        ("help", "Show this help", "mythic help")
    ]
    
    for cmd, desc, usage in commands:
        table.add_row(cmd, desc, usage)
    
    console.print(table)


def create_debug_config():
    """Create a debug configuration with all necessary sections."""
    class DebugConfig:
        debug_mode = True
        
        # Logging configuration
        logging = type('obj', (object,), {
            'level': 'DEBUG',
            'format': 'rich',
            'console_output': True
        })()
        
        # ASR configuration
        asr = type('obj', (object,), {
            'enable_asr': True,
            'model_name': 'base',
            'model_size': 'tiny',
            'language': 'en',
            'chunk_length': 30.0,
            'sample_rate': 16000,
            'channels': 1,
            'audio_format': 'paInt16'
        })()
        
        # TTS configuration
        tts = type('obj', (object,), {
            'voice_path': 'ljspeech-high',
            'sample_rate': 22050,
            'channels': 1,
            'audio_format': 'paInt16',
            'enable_audio': True,
            'AVAILABLE_VOICES': {
                'amy-low': 'en/en_US/amy/low',
                'amy-medium': 'en/en_US/amy/medium',
                'amy-high': 'en/en_US/amy/high',
                'jenny-low': 'en/en_US/jenny/low',
                'jenny-medium': 'en/en_US/jenny/medium',
                'jenny-high': 'en/en_US/jenny/high',
                'karen-low': 'en/en_US/karen/low',
                'karen-medium': 'en/en_US/karen/medium',
                'karen-high': 'en/en_US/karen/high',
                'chris-low': 'en/en_US/chris/low',
                'chris-medium': 'en/en_US/chris/medium',
                'chris-high': 'en/en_US/chris/high'
            }
        })()
        
        # LLM configuration
        llm = type('obj', (object,), {
            'model_repo': 'MaziyarPanahi/gemma-3-1b-it-GGUF',
            'model_filename': 'gemma-3-1b-it.Q4_K_M.gguf',
            'max_tokens': 150,
            'temperature': 0.7,
            'context_window': 512
        })()
        
        # Summarization configuration
        summarization = type('obj', (object,), {
            'model_repo': 'MaziyarPanahi/gemma-3-1b-it-GGUF',
            'model_filename': 'gemma-3-1b-it.Q4_K_M.gguf',
            'max_tokens': 80,
            'temperature': 0.0
        })()
        
        # Conversation configuration
        conversation = type('obj', (object,), {
            'max_conversation_length': 12,
            'max_tokens_per_message': 200,
            'memory_compression_threshold': 8,
            'auto_summarize_interval': 4
        })()
        
        # UI configuration
        ui = type('obj', (object,), {
            'enable_colors': True,
            'enable_progress_bars': False,  # Disabled to avoid Task issues
            'enable_animations': True,
            'theme': 'default'
        })()
        
        def to_dict(self):
            """Convert config to dictionary for compatibility."""
            return {
                'debug_mode': self.debug_mode,
                'logging': {'level': self.logging.level, 'format': self.logging.format, 'console_output': self.logging.console_output},
                'asr': {k: v for k, v in self.asr.__dict__.items() if not k.startswith('_')},
                'tts': {k: v for k, v in self.tts.__dict__.items() if not k.startswith('_')},
                'llm': {k: v for k, v in self.llm.__dict__.items() if not k.startswith('_')},
                'summarization': {k: v for k, v in self.summarization.__dict__.items() if not k.startswith('_')},
                'conversation': {k: v for k, v in self.conversation.__dict__.items() if not k.startswith('_')},
                'ui': {k: v for k, v in self.ui.__dict__.items() if not k.startswith('_')}
            }
    
    return DebugConfig()


def create_orchestrator(config=None):
    """Create an orchestrator instance."""
    from ..core import get_chatbot_orchestrator
    ChatbotOrchestrator = get_chatbot_orchestrator()
    
    if config and hasattr(config, 'debug_mode') and config.debug_mode:
        console.print("Creating orchestrator with debug configuration", style="dim cyan")
    
    return ChatbotOrchestrator(config)


def show_debug_message():
    """Show debug mode enabled message."""
    console.print("Debug mode enabled - verbose logging active", style="bold yellow")


def initialize_system(orchestrator):
    """Initialize the Mythic system."""
    if hasattr(orchestrator, 'config') and orchestrator.config and hasattr(orchestrator.config, 'debug_mode') and orchestrator.config.debug_mode:
        console.print("Starting system initialization with debug mode", style="dim cyan")
    
    if orchestrator.initialize_workers():
        console.print("Mythic system initialized successfully!", style="bold green")
        return True
    else:
        console.print("Failed to initialize Mythic system", style="bold red")
        return False


def show_system_status(orchestrator):
    """Show system status."""
    try:
        status_info = {
            "System": "Mythic-Lite Chatbot",
            "Version": "1.0.0",
            "Environment": "development",
            "Debug Mode": "true" if orchestrator.debug_mode else "false",
            "LLM Status": orchestrator.llm_worker.get_status() if orchestrator.is_initialized() else "Not available",
            "TTS Status": orchestrator.tts_worker.get_status() if orchestrator.is_initialized() else "Not available",
            "ASR Status": orchestrator.asr_worker.get_status() if orchestrator.is_initialized() else "Not available",
            "Summarization Status": orchestrator.summarization_worker.get_status() if orchestrator.is_initialized() else "Not available",
        }
        
        # Display status in a beautiful table
        table = Table(
            title="System Status",
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
            border_style="cyan"
        )
        table.add_column("Component", style="cyan bold", width=20)
        table.add_column("Status", style="white")
        
        for key, value in status_info.items():
            # Color-code status values
            if "enabled" in str(value).lower() or "success" in str(value).lower():
                status_style = "green"
            elif "disabled" in str(value).lower() or "error" in str(value).lower():
                status_style = "red"
            elif "warning" in str(value).lower():
                status_style = "yellow"
            else:
                status_style = "white"
            
            table.add_row(key, Text(str(value), style=status_style))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"Failed to show status: {e}", style="red")