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
@click.option('--interactive', is_flag=True, help='Enable interactive mode')
@click.option('--test-tts', is_flag=True, help='Test TTS system')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def chat(ctx, interactive: bool, test_tts: bool, debug: bool):
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
        
        # Initialize the system
        if initialize_system(orchestrator):
            # Run in chat mode
            console.print("Launching Mythic...", style="green")
            console.print("Starting text-based chat...", style="cyan")
            
            # Start the actual chat interface
            orchestrator.run_chatbot()
        else:
            console.print("Failed to initialize system", style="bold red")
            ctx.exit(1)
        
    except KeyboardInterrupt:
        console.print("\nChat interrupted - Mythic returns to the shadows...", style="yellow")
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
            orchestrator.run_asr_only()
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
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def init(ctx, debug: bool):
    """Initialize the Mythic system."""
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
            # Show status
            show_system_status(orchestrator)
            
            # Ask if user wants to start chat
            from .common import confirm_action
            if confirm_action("Would you like to start a chat now? (y/n): "):
                console.print("Starting chat...", style="green")
                orchestrator.run_chatbot()
        else:
            console.print("Failed to initialize system", style="bold red")
            ctx.exit(1)
                
    except Exception as e:
        console.print(f"Failed to initialize system: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()


@click.command()
@click.option('--voices', is_flag=True, help='Show available TTS voices')
@click.option('--system', is_flag=True, help='Show system information')
@click.option('--quick-start', is_flag=True, help='Show quick start guide')
@click.option('--troubleshooting', is_flag=True, help='Show troubleshooting guide')
@click.pass_context
def config(ctx, voices: bool, system: bool, quick_start: bool, troubleshooting: bool):
    """Show current configuration and system information."""
    logger = ctx.obj['logger']
    
    try:
        from .config_manager import get_config_manager
        config_manager = get_config_manager()
        
        if voices:
            config_manager.show_available_voices()
        elif system:
            config_manager.show_system_info()
        elif quick_start:
            config_manager.show_quick_start()
        elif troubleshooting:
            config_manager.show_troubleshooting()
        else:
            # Show main configuration
            config_manager.show_configuration()
            
            # Ask if user wants to start chat
            from .common import confirm_action
            if confirm_action("Would you like to start a chat now? (y/n): "):
                console.print("Starting chat...", style="green")
                orchestrator = create_orchestrator(None)
                if initialize_system(orchestrator):
                    orchestrator.run_chatbot()
                orchestrator.cleanup()
        
    except Exception as e:
        console.print(f"Failed to show configuration: {e}", style="red")
        ctx.exit(1)


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def status(ctx, debug: bool):
    """Show system status."""
    try:
        console.print("System Status", style="bold cyan")
        
        if debug:
            console.print("Debug mode enabled - verbose logging active", style="bold yellow")
        
        # Create orchestrator for status display
        debug_config = None
        if debug:
            from .cli_helpers import create_debug_config
            debug_config = create_debug_config()
        
        orchestrator = create_orchestrator(debug_config)
        show_system_status(orchestrator)
        
        # Ask if user wants to start chat
        from .common import confirm_action
        if confirm_action("Would you like to start a chat now? (y/n): "):
            console.print("Starting chat...", style="green")
            if initialize_system(orchestrator):
                orchestrator.run_chatbot()
        
        # Cleanup
        if 'orchestrator' in locals():
            orchestrator.cleanup()
        
    except Exception as e:
        console.print(f"Failed to show status: {e}", style="red")
        ctx.exit(1)


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def benchmark(ctx, debug: bool):
    """Run comprehensive system benchmark."""
    try:
        console.print("MYTHIC-LITE BENCHMARK MODE", style="bold blue")
        console.print("=" * 80, style="bold blue")
        
        if debug:
            console.print("Debug mode enabled - verbose logging active", style="bold yellow")
        
        # Create orchestrator for benchmark
        debug_config = None
        if debug:
            from .cli_helpers import create_debug_config
            debug_config = create_debug_config()
        
        orchestrator = create_orchestrator(debug_config)
        
        # Run the comprehensive benchmark
        orchestrator._run_benchmark_mode()
        
        console.print("\nBenchmark completed successfully!", style="bold green")
        
        # Ask if user wants to start chat
        from .common import confirm_action
        if confirm_action("Would you like to start a chat now? (y/n): "):
            console.print("Starting chat...", style="green")
            if initialize_system(orchestrator):
                orchestrator.run_chatbot()
        
        # Cleanup
        if 'orchestrator' in locals():
            orchestrator.cleanup()
        
    except Exception as e:
        console.print(f"Benchmark failed: {e}", style="red")
        ctx.exit(1)


@click.command()
@click.pass_context
def help(ctx):
    """Show detailed help information."""
    from .cli_helpers import print_banner, print_help_table
    
    print_banner()
    print_help_table()
    
    console.print("\nDetailed Information:", style="bold cyan")
    console.print("• Text Chat: Use mythic chat for keyboard conversations")
    console.print("• Voice Chat: Use mythic voice for voice conversations")
    console.print("• System Status: Use mythic status to check system health")
    console.print("• System Benchmark: Use mythic benchmark for comprehensive analysis")
    console.print("• Initialization: Use mythic init to set up the system")
    
    console.print("\nTips:", style="yellow")
    console.print("• Start with mythic init if this is your first time")
    console.print("• Use mythic status to verify all systems are working")
    console.print("• Use mythic benchmark for detailed performance analysis")
    console.print("• For voice conversations, ensure your microphone is working")
    console.print("• Just run mythic without arguments to run setup then start voice mode!")
    console.print("• The default behavior is: Setup → Voice Mode (hands-free operation)")


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def test_tts(ctx, debug: bool):
    """Test the TTS system."""
    try:
        console.print("Testing TTS system...", style="yellow")
        
        if debug:
            console.print("Debug mode enabled - verbose logging active", style="bold yellow")
        
        # Create orchestrator with debug config if enabled
        debug_config = None
        if debug:
            from .cli_helpers import create_debug_config
            debug_config = create_debug_config()
        
        orchestrator = create_orchestrator(debug_config)
        
        if initialize_system(orchestrator):
            if orchestrator.tts_worker.initialize():
                if orchestrator.tts_worker.is_tts_enabled():
                    test_text = "This is a test of the text-to-speech system."
                    audio_data = orchestrator.tts_worker.text_to_speech_stream(test_text)
                    
                    if audio_data:
                        console.print("TTS test successful!", style="green")
                        console.print("Playing test audio...", style="cyan")
                        orchestrator.tts_worker.play_audio_stream(audio_data)
                    else:
                        console.print("TTS test failed - no audio generated", style="red")
                else:
                    console.print("TTS is disabled due to errors", style="yellow")
            else:
                console.print("TTS system failed to initialize", style="red")
        else:
            console.print("Failed to initialize system", style="bold red")
            
    except Exception as e:
        console.print(f"TTS test failed: {e}", style="red")
        ctx.exit(1)
    finally:
        if 'orchestrator' in locals():
            orchestrator.cleanup()