"""
CLI command implementations for Mythic-Lite chatbot system.

Separated from main CLI structure for better organization and maintainability.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.box import ROUNDED
from typing import Optional, Any

from .cli_helpers import create_orchestrator, initialize_system, show_system_status

console = Console()


@click.command()
@click.option('--character', '-c', default=None, help='Character to use (mythic, sage, or none for generic)')
@click.option('--interactive', is_flag=True, help='Enable interactive mode')
@click.option('--test-tts', is_flag=True, help='Test TTS system')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def chat(ctx, character: Optional[str], interactive: bool, test_tts: bool, debug: bool):
    """Start a text-based chat with Mythic."""
    logger = ctx.obj['logger']
    
    try:
        console.print("Starting text-based chat mode...", style="bold cyan")
        
        if interactive:
            console.print("Interactive mode enabled", style="green")
        
        if debug:
            console.print("Debug mode enabled - verbose logging active", style="bold yellow")
        
        # Create orchestrator with debug config if enabled
        debug_config = None
        if debug:
            from .cli_helpers import create_debug_config
            debug_config = create_debug_config()
        
        orchestrator = create_orchestrator(debug_config)
        
        # Set character if specified
        if character:
            if character.lower() == 'none':
                orchestrator.config.conversation.character_name = None
                orchestrator.config.conversation.system_prompt = "You are a helpful AI assistant. Be direct, practical, and maintain a professional tone."
                orchestrator.config.conversation.user_prefix = "User: "
                orchestrator.config.conversation.assistant_prefix = "Assistant: "
                console.print("Using generic AI assistant", style="green")
            else:
                orchestrator.config.conversation.character_name = character.lower()
                console.print(f"Using character: {character}", style="green")
        
        # Initialize the system
        if initialize_system(orchestrator):
            # Display character info
            if orchestrator.config.conversation.character_name:
                from mythic_lite.core import get_character
                character_config = get_character(orchestrator.config.conversation.character_name)
                if character_config:
                    console.print(f"🤖 Character: {character_config.personality.name}", style="bold cyan")
                    console.print(f"📝 Description: {character_config.personality.description}", style="cyan")
                    console.print(f"🎭 Personality: {', '.join(character_config.personality.personality_traits[:3])}...", style="cyan")
                else:
                    console.print(f"⚠️ Character '{orchestrator.config.conversation.character_name}' not found, using generic assistant", style="yellow")
            else:
                console.print("🤖 Using generic AI assistant", style="cyan")
            
            # Run in chat mode
            console.print("Launching chat...", style="green")
            console.print("Starting text-based chat...", style="cyan")
            
            # Start the actual chat interface
            orchestrator.run_chatbot()
        else:
            console.print("Failed to initialize system", style="bold red")
            ctx.exit(1)
        
    except KeyboardInterrupt:
        console.print("\nChat interrupted - returning to main menu...", style="yellow")
    except Exception as e:
        console.print(f"Failed to start chat: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@click.command()
@click.option('--auto-start', is_flag=True, help='Start voice recording automatically')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def voice(ctx, auto_start: bool, debug: bool):
    """Start a voice conversation with Mythic."""
    logger = ctx.obj['logger']
    
    try:
        console.print("Starting voice conversation mode...", style="bold cyan")
        
        if debug:
            console.print("Debug mode enabled - verbose logging active", style="bold yellow")
        
        # Create orchestrator with debug config if enabled
        debug_config = None
        if debug:
            from .cli_helpers import create_debug_config
            debug_config = create_debug_config()
        
        orchestrator = create_orchestrator(debug_config)
        
        # Initialize the system
        if initialize_system(orchestrator):
            # Run ASR-only mode
            console.print("Launching Mythic in voice mode...", style="green")
            console.print("Starting voice conversation...", style="cyan")
            
            # Start the actual voice interface
            orchestrator.run_voice_mode()
        else:
            console.print("Failed to initialize system", style="bold red")
            ctx.exit(1)
        
    except KeyboardInterrupt:
        console.print("\nVoice mode interrupted - Mythic returns to the shadows...", style="yellow")
    except Exception as e:
        console.print(f"Failed to start voice mode: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@click.command()
@click.option('--force', is_flag=True, help='Force reinitialization')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def init(ctx, force: bool, debug: bool):
    """Initialize the Mythic system."""
    logger = ctx.obj['logger']
    
    try:
        console.print("Initializing Mythic System", style="bold cyan")
        
        if debug:
            console.print("Debug mode enabled - verbose logging active", style="bold yellow")
        
        # Create orchestrator with debug config if enabled
        debug_config = None
        if debug:
            from .cli_helpers import create_debug_config
            debug_config = create_debug_config()
        
        orchestrator = create_orchestrator(debug_config)
        
        if initialize_system(orchestrator):
            console.print("System initialized successfully", style="bold green")
            show_system_status(orchestrator)
        else:
            console.print("Failed to initialize system", style="bold red")
            ctx.exit(1)
        
    except Exception as e:
        console.print(f"Initialization failed: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@click.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--edit', is_flag=True, help='Edit configuration')
@click.option('--reset', is_flag=True, help='Reset to default configuration')
@click.pass_context
def config(ctx, show: bool, edit: bool, reset: bool):
    """Manage system configuration."""
    logger = ctx.obj['logger']
    
    try:
        if show:
            console.print("Configuration management not yet implemented", style="yellow")
        elif edit:
            console.print("Configuration editing not yet implemented", style="yellow")
        elif reset:
            console.print("Configuration reset not yet implemented", style="yellow")
        else:
            console.print("Use --show, --edit, or --reset to manage configuration", style="cyan")
        
    except Exception as e:
        console.print(f"Configuration operation failed: {e}", style="red")
        ctx.exit(1)


@click.command()
@click.pass_context
def status(ctx):
    """Show system status."""
    logger = ctx.obj['logger']
    
    try:
        console.print("System Status", style="bold cyan")
        
        # Create orchestrator
        orchestrator = create_orchestrator()
        
        # Show status
        show_system_status(orchestrator)
        
    except Exception as e:
        console.print(f"Failed to get system status: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@click.command()
@click.option('--full', is_flag=True, help='Run full benchmark suite')
@click.option('--quick', is_flag=True, help='Run quick benchmark')
@click.pass_context
def benchmark(ctx, full: bool, quick: bool):
    """Run system benchmarks."""
    logger = ctx.obj['logger']
    
    try:
        console.print("Running system benchmark...", style="bold cyan")
        
        # Create orchestrator
        orchestrator = create_orchestrator()
        
        # Initialize system
        if initialize_system(orchestrator):
            # Run benchmark
            results = orchestrator.run_benchmark()
            
            if results:
                console.print("Benchmark completed successfully", style="bold green")
                console.print(f"Overall score: {results.get('overall_score', 0)}/100", style="cyan")
            else:
                console.print("Benchmark failed", style="bold red")
        else:
            console.print("Failed to initialize system for benchmark", style="bold red")
            ctx.exit(1)
        
    except Exception as e:
        console.print(f"Benchmark failed: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@click.command()
@click.pass_context
def help(ctx):
    """Show help information."""
    logger = ctx.obj['logger']
    
    help_text = """
Mythic-Lite AI Chatbot System

Available Commands:
  chat      - Start text-based chat
  voice     - Start voice conversation
  init      - Initialize system
  config    - Manage configuration
  status    - Show system status
  benchmark - Run system benchmarks
  help      - Show this help

For more information about a command, use:
  mythic <command> --help
    """
    
    console.print(Panel(help_text, title="Help", box=ROUNDED))


@click.command()
@click.option('--text', default="Hello, this is a TTS test.", help='Text to synthesize')
@click.pass_context
def test_tts(ctx, text: str):
    """Test the TTS system."""
    logger = ctx.obj['logger']
    
    try:
        console.print(f"Testing TTS with text: {text}", style="bold cyan")
        
        # Create orchestrator
        orchestrator = create_orchestrator()
        
        # Initialize system
        if initialize_system(orchestrator):
            # Test TTS
            if orchestrator.tts_worker.speak(text):
                console.print("TTS test successful", style="bold green")
            else:
                console.print("TTS test failed", style="bold red")
        else:
            console.print("Failed to initialize system for TTS test", style="bold red")
            ctx.exit(1)
        
    except Exception as e:
        console.print(f"TTS test failed: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()