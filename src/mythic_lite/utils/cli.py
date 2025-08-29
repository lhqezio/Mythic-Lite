"""
Beautiful command-line interface for Mythic-Lite chatbot system.
Provides an intuitive, modern CLI with rich output and clear commands.
"""

import sys
import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from rich.columns import Columns
from rich.box import ROUNDED

from .logger import setup_logging, get_logger

# Rich console for beautiful output
console = Console()


def print_banner():
    """Print the beautiful Mythic-Lite banner."""
    banner_text = Text()
    banner_text.append("🔥 ", style="red bold")
    banner_text.append("MYTHIC-LITE", style="magenta bold")
    banner_text.append(" 🔥", style="red bold")
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
    """Print a beautiful help table."""
    table = Table(
        title="🚀 Available Commands",
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
        console.print("🐛 Creating orchestrator with debug configuration", style="dim cyan")
    
    return ChatbotOrchestrator(config)


def show_debug_message():
    """Show debug mode enabled message."""
    console.print("🐛 Debug mode enabled - verbose logging active", style="bold yellow")


def initialize_system(orchestrator):
    """Initialize the Mythic system."""
    if hasattr(orchestrator, 'config') and orchestrator.config and hasattr(orchestrator.config, 'debug_mode') and orchestrator.config.debug_mode:
        console.print("🐛 Starting system initialization with debug mode", style="dim cyan")
    
    if orchestrator.initialize_workers():
        console.print("🎉 Mythic system initialized successfully!", style="bold green")
        return True
    else:
        console.print("💥 Failed to initialize Mythic system", style="bold red")
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
            title="📊 System Status",
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
        console.print(f"❌ Failed to show status: {e}", style="red")


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx, debug: bool, no_colors: bool, version: bool):
    """🔥 MYTHIC-LITE: 19th Century Mercenary AI Chatbot
    
    Experience conversations with a fierce female warrior from the Victorian era.
    All processing happens locally on your device for complete privacy.
    """
    # Handle version flag
    if version:
        console.print("🔥 MYTHIC-LITE", style="bold magenta")
        console.print("v1.0.0", style="cyan")
        sys.exit(0)
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Setup logging with debug mode if enabled
    if debug:
        logger = setup_logging("mythic-cli", create_debug_config())
        show_debug_message()
    else:
        logger = setup_logging("mythic-cli", None)
    
    ctx.obj['logger'] = logger
    
    # If no command specified, run setup then start in voice mode
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("🚀 Starting Mythic-Lite...", style="green")
        console.print("🔧 No command specified - running setup then starting voice mode", style="cyan")
        
        try:
            # First run initialization
            console.print("\n🔧 Initializing Mythic System", style="bold cyan")
            
            # Create orchestrator with debug config if enabled
            debug_config = create_debug_config() if debug else None
            orchestrator = create_orchestrator(debug_config)
            
            if initialize_system(orchestrator):
                # Show status
                show_system_status(orchestrator)
                
                # Now start in voice mode
                console.print("\n🎤 Starting voice conversation mode...", style="bold cyan")
                console.print("🚀 Launching Mythic in voice mode...", style="green")
                console.print("🎤 Starting voice conversation...", style="cyan")
                
                # Start the actual voice interface
                orchestrator.run_asr_only()
                
            else:
                console.print("💥 Failed to initialize Mythic system", style="bold red")
                console.print("💡 Try using 'mythic init' to troubleshoot", style="cyan")
                sys.exit(1)
                        

                    
        except KeyboardInterrupt:
            console.print("\n👋 Voice mode interrupted - Mythic returns to the shadows...", style="yellow")
        except Exception as e:
            console.print(f"❌ Failed to start voice mode: {e}", style="red")
            console.print("💡 Try using a specific command like 'mythic voice' or 'mythic help'", style="cyan")
            sys.exit(1)
        finally:
            if 'orchestrator' in locals():
                orchestrator.cleanup()


@cli.command()
@click.option('--interactive', is_flag=True, help='Enable interactive mode')
@click.option('--test-tts', is_flag=True, help='Test TTS system')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def chat(ctx, interactive: bool, test_tts: bool, debug: bool):
    """💬 Start a text-based chat with Mythic."""
    logger = ctx.obj['logger']
    
    try:
        print_banner()
        console.print("💬 Starting text-based chat mode...", style="bold cyan")
        
        if interactive:
            console.print("🎯 Interactive mode enabled", style="green")
        
        if debug:
            show_debug_message()
        
        # Create orchestrator with debug config if enabled
        debug_config = create_debug_config() if debug else None
        orchestrator = create_orchestrator(debug_config)
        
        # Initialize the system
        if initialize_system(orchestrator):
            # Run in chat mode
            console.print("🚀 Launching Mythic...", style="green")
            console.print("💬 Starting text-based chat...", style="cyan")
            
            # Start the actual chat interface
            orchestrator.run_chatbot()
        else:
            console.print("💥 Failed to initialize system", style="bold red")
            sys.exit(1)
        
    except KeyboardInterrupt:
        console.print("\n👋 Chat interrupted - Mythic returns to the shadows...", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to start chat: {e}", style="red")
        sys.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@cli.command()
@click.option('--auto-start', is_flag=True, help='Start voice recording automatically')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def voice(ctx, auto_start: bool, debug: bool):
    """🎤 Start a voice conversation with Mythic."""
    logger = ctx.obj['logger']
    
    try:
        print_banner()
        console.print("🎤 Starting voice conversation mode...", style="bold cyan")
        
        if debug:
            show_debug_message()
        
        # Create orchestrator with debug config if enabled
        debug_config = create_debug_config() if debug else None
        orchestrator = create_orchestrator(debug_config)
        
        # Initialize the system
        if initialize_system(orchestrator):
            # Run ASR-only mode
            console.print("🚀 Launching Mythic in voice mode...", style="green")
            console.print("🎤 Starting voice conversation...", style="cyan")
            
            # Start the actual voice interface
            orchestrator.run_asr_only()
        else:
            console.print("💥 Failed to initialize system", style="bold red")
            sys.exit(1)
        
    except KeyboardInterrupt:
        console.print("\n👋 Voice mode interrupted - Mythic returns to the shadows...", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to start voice mode: {e}", style="red")
        sys.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def init(ctx, debug: bool):
    """🔧 Initialize the Mythic system."""
    try:
        print_banner()
        console.print("🔧 Initializing Mythic System", style="bold cyan")
        
        if debug:
            show_debug_message()
        
        # Create orchestrator with debug config if enabled
        debug_config = create_debug_config() if debug else None
        orchestrator = create_orchestrator(debug_config)
        
        if initialize_system(orchestrator):
            # Show status
            show_system_status(orchestrator)
            
            # Ask if user wants to start chat
            console.print("\n💬 Would you like to start a chat now? (y/n)", style="cyan")
            try:
                choice = input("Enter choice: ").lower().strip()
                if choice in ['y', 'yes']:
                    console.print("🚀 Starting chat...", style="green")
                    orchestrator.run_chatbot()
            except KeyboardInterrupt:
                console.print("\n👋 Returning to main menu...", style="yellow")
        else:
            console.print("💥 Failed to initialize system", style="bold red")
            sys.exit(1)
                
    except Exception as e:
        console.print(f"❌ Failed to initialize system: {e}", style="red")
        sys.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@cli.command()
@click.pass_context
def config(ctx):
    """⚙️ Show current configuration."""
    logger = ctx.obj['logger']
    
    try:
        print_banner()
        console.print("⚙️ Current Configuration", style="bold cyan")
        
        # Use lazy import to avoid circular dependencies
        from ..core.config import get_config
        config = get_config()
        config_dict = config.to_dict()
        
        # Display configuration in a beautiful table
        table = Table(
            title="⚙️ Configuration",
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
            border_style="cyan"
        )
        table.add_column("Setting", style="cyan bold", width=30)
        table.add_column("Value", style="white")
        
        for key, value in config_dict.items():
            if isinstance(value, dict):
                # Handle nested config sections
                for subkey, subvalue in value.items():
                    table.add_row(f"{key}.{subkey}", str(subvalue))
            else:
                table.add_row(key, str(value))
        
        console.print(table)
        
        # Ask if user wants to start chat
        console.print("\n💬 Would you like to start a chat now? (y/n)", style="cyan")
        try:
            choice = input("Choice: ").lower().strip()
            if choice in ['y', 'yes']:
                console.print("🚀 Starting chat...", style="green")
                orchestrator = create_orchestrator(None)
                if initialize_system(orchestrator):
                    orchestrator.run_chatbot()
                orchestrator.cleanup()
        except KeyboardInterrupt:
            console.print("\n👋 Returning to main menu...", style="yellow")
        
    except Exception as e:
        console.print(f"❌ Failed to show configuration: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def status(ctx, debug: bool):
    """📊 Show system status."""
    try:
        print_banner()
        console.print("📊 System Status", style="bold cyan")
        
        if debug:
            show_debug_message()
        
        # Create orchestrator for status display
        debug_config = create_debug_config() if debug else None
        orchestrator = create_orchestrator(debug_config)
        show_system_status(orchestrator)
        
        # Ask if user wants to start chat
        console.print("\n💬 Would you like to start a chat now? (y/n)", style="cyan")
        try:
            choice = input("Enter choice: ").lower().strip()
            if choice in ['y', 'yes']:
                console.print("🚀 Starting chat...", style="green")
                if initialize_system(orchestrator):
                    orchestrator.run_chatbot()
        except KeyboardInterrupt:
            console.print("\n👋 Returning to main menu...", style="yellow")
        finally:
            if 'orchestrator' in locals():
                orchestrator.cleanup()
        
    except Exception as e:
        console.print(f"❌ Failed to show status: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def benchmark(ctx, debug: bool):
    """🚀 Run comprehensive system benchmark."""
    try:
        print_banner()
        console.print("🚀 MYTHIC-LITE BENCHMARK MODE", style="bold blue")
        console.print("=" * 80, style="bold blue")
        
        if debug:
            show_debug_message()
        
        # Create orchestrator for benchmark
        debug_config = create_debug_config() if debug else None
        orchestrator = create_orchestrator(debug_config)
        
        # Run the comprehensive benchmark
        orchestrator._run_benchmark_mode()
        
        console.print("\n✅ Benchmark completed successfully!", style="bold green")
        
        # Ask if user wants to start chat
        console.print("\n💬 Would you like to start a chat now? (y/n)", style="cyan")
        try:
            choice = input("Enter choice: ").lower().strip()
            if choice in ['y', 'yes']:
                console.print("🚀 Starting chat...", style="green")
                if initialize_system(orchestrator):
                    orchestrator.run_chatbot()
        except KeyboardInterrupt:
            console.print("\n👋 Returning to main menu...", style="yellow")
        finally:
            if 'orchestrator' in locals():
                orchestrator.cleanup()
        
    except Exception as e:
        console.print(f"❌ Benchmark failed: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.pass_context
def help(ctx):
    """❓ Show detailed help information."""
    print_banner()
    print_help_table()
    
    console.print("\n🔍 Detailed Information:", style="bold cyan")
    console.print("• Text Chat: Use mythic chat for keyboard conversations")
    console.print("• Voice Chat: Use mythic voice for voice conversations")
    console.print("• System Status: Use mythic status to check system health")
    console.print("• System Benchmark: Use mythic benchmark for comprehensive analysis")
    console.print("• Initialization: Use mythic init to set up the system")
    
    console.print("\n💡 Tips:", style="yellow")
    console.print("• Start with mythic init if this is your first time")
    console.print("• Use mythic status to verify all systems are working")
    console.print("• Use mythic benchmark for detailed performance analysis")
    console.print("• For voice conversations, ensure your microphone is working")
    console.print("• Just run mythic without arguments to run setup then start voice mode!")
    console.print("• The default behavior is: Setup → Voice Mode (hands-free operation)")


@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def test_tts(ctx, debug: bool):
    """🔊 Test the TTS system."""
    try:
        console.print("🔊 Testing TTS system...", style="yellow")
        
        if debug:
            show_debug_message()
        
        # Create orchestrator with debug config if enabled
        debug_config = create_debug_config() if debug else None
        orchestrator = create_orchestrator(debug_config)
        
        if initialize_system(orchestrator):
            if orchestrator.tts_worker.initialize():
                if orchestrator.tts_worker.is_tts_enabled():
                    test_text = "This is a test of the text-to-speech system."
                    audio_data = orchestrator.tts_worker.text_to_speech_stream(test_text)
                    
                    if audio_data:
                        console.print("✅ TTS test successful!", style="green")
                        console.print("🔊 Playing test audio...", style="cyan")
                        orchestrator.tts_worker.play_audio_stream(audio_data)
                    else:
                        console.print("❌ TTS test failed - no audio generated", style="red")
                else:
                    console.print("⚠️  TTS is disabled due to errors", style="yellow")
            else:
                console.print("❌ TTS system failed to initialize", style="red")
        else:
            console.print("💥 Failed to initialize system", style="bold red")
            
    except Exception as e:
        console.print(f"❌ TTS test failed: {e}", style="red")
        sys.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


if __name__ == "__main__":
    cli()
