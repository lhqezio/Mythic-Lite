"""
Configuration management module for Mythic-Lite chatbot system.
Provides a clean interface for managing and displaying configuration settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED
from rich.text import Text

from ..core.config import get_config

console = Console()


class ConfigManager:
    """Manages configuration display and interaction."""
    
    def __init__(self):
        self.config = get_config()
    
    def show_configuration(self, show_details: bool = False):
        """Display current configuration in a clean, organized format."""
        console.print("Current Configuration", style="bold cyan")
        
        # Group configuration by category
        config_groups = {
            "System": {
                "Debug Mode": self.config.debug_mode,
                "Environment": "development"
            },
            "Language Models": {
                "LLM Model": f"{self.config.llm.model_repo}/{self.config.llm.model_filename}",
                "Max Tokens": self.config.llm.max_tokens,
                "Temperature": self.config.llm.temperature,
                "Context Window": self.config.llm.context_window
            },
            "Audio & Speech": {
                "TTS Voice": self.config.tts.voice_path,
                "TTS Sample Rate": f"{self.config.tts.sample_rate} Hz",
                "ASR Model": f"{self.config.asr.model_name}-{self.config.asr.model_size}",
                "ASR Language": self.config.asr.language,
                "ASR Enabled": self.config.asr.enable_asr
            },
            "Memory & Conversation": {
                "Max Conversation Length": self.config.conversation.max_conversation_length,
                "Max Tokens Per Message": self.config.conversation.max_tokens_per_message,
                "Memory Compression Threshold": self.config.conversation.memory_compression_threshold,
                "Auto Summarize Interval": self.config.conversation.auto_summarize_interval
            },
            "Logging": {
                "Log Level": self.config.logging.level,
                "Log Format": self.config.logging.format,
                "Console Output": self.config.logging.console_output
            }
        }
        
        # Display configuration in organized tables
        for group_name, settings in config_groups.items():
            self._display_config_group(group_name, settings, show_details)
            console.print()  # Add spacing between groups
    
    def _display_config_group(self, group_name: str, settings: Dict[str, Any], show_details: bool):
        """Display a configuration group."""
        table = Table(
            title=group_name,
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
            border_style="cyan"
        )
        table.add_column("Setting", style="cyan bold", width=30)
        table.add_column("Value", style="white")
        
        for key, value in settings.items():
            # Color-code values based on type and status
            if isinstance(value, bool):
                value_style = "green" if value else "red"
            elif isinstance(value, str) and any(status in str(value).lower() for status in ["enabled", "success", "true"]):
                value_style = "green"
            elif isinstance(value, str) and any(status in str(value).lower() for status in ["disabled", "error", "false"]):
                value_style = "red"
            else:
                value_style = "white"
            
            table.add_row(key, Text(str(value), style=value_style))
        
        console.print(table)
    
    def show_available_voices(self):
        """Display available TTS voices."""
        console.print("Available TTS Voices", style="bold cyan")
        
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
            border_style="cyan"
        )
        table.add_column("Voice ID", style="cyan bold", width=20)
        table.add_column("Description", style="white")
        table.add_column("Quality", style="white")
        
        voices = self.config.tts.AVAILABLE_VOICES
        for voice_id, path in voices.items():
            # Extract quality from voice ID
            quality = voice_id.split('-')[-1] if '-' in voice_id else "standard"
            description = f"Voice from {path}"
            
            table.add_row(voice_id, description, quality)
        
        console.print(table)
    
    def show_system_info(self):
        """Display system information."""
        console.print("System Information", style="bold cyan")
        
        info_panel = Panel(
            Text("Mythic-Lite AI Chatbot\n", style="bold magenta") +
            Text("Version: 1.0.0\n", style="cyan") +
            Text("Environment: Development\n", style="white") +
            Text("Architecture: Local Processing\n", style="white") +
            Text("Privacy: Complete (No external API calls)", style="green"),
            title="System Overview",
            border_style="magenta",
            box=ROUNDED
        )
        
        console.print(info_panel)
    
    def show_quick_start(self):
        """Display quick start guide."""
        console.print("Quick Start Guide", style="bold cyan")
        
        steps = [
            ("1. Initialize", "mythic init", "Set up the system"),
            ("2. Check Status", "mythic status", "Verify all systems"),
            ("3. Start Chat", "mythic chat", "Begin conversation"),
            ("4. Voice Mode", "mythic voice", "Voice conversation"),
            ("5. Benchmark", "mythic benchmark", "Test performance")
        ]
        
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
            border_style="cyan"
        )
        table.add_column("Step", style="cyan bold", width=15)
        table.add_column("Command", style="white", width=20)
        table.add_column("Description", style="white")
        
        for step, command, description in steps:
            table.add_row(step, command, description)
        
        console.print(table)
    
    def show_troubleshooting(self):
        """Display troubleshooting information."""
        console.print("Troubleshooting Guide", style="bold cyan")
        
        issues = [
            ("Audio Issues", "Check microphone permissions and audio drivers"),
            ("Model Loading", "Ensure models are downloaded and accessible"),
            ("Performance", "Use 'mythic benchmark' to identify bottlenecks"),
            ("Memory Issues", "Check available RAM and disk space"),
            ("Dependencies", "Verify all required packages are installed")
        ]
        
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
            border_style="cyan"
        )
        table.add_column("Issue", style="cyan bold", width=20)
        table.add_column("Solution", style="white")
        
        for issue, solution in issues:
            table.add_row(issue, solution)
        
        console.print(table)


def get_config_manager() -> ConfigManager:
    """Get a configuration manager instance."""
    return ConfigManager()