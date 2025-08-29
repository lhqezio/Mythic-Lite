"""
Command-line interface for Mythic-Lite chatbot system.

Provides a clean, professional CLI with clear commands and logical organization.
"""

import sys
import click
from pathlib import Path
from typing import Optional
from rich.console import Console

from .logger import setup_logging
from .cli_helpers import print_banner, create_debug_config, create_orchestrator, initialize_system, show_system_status
from .cli_commands import chat, voice, init, config, status, benchmark, help, test_tts

# Rich console for beautiful output
console = Console()


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx, debug: bool, no_colors: bool, version: bool):
    """MYTHIC-LITE: Professional AI Chatbot System
    
    A modular, enterprise-ready AI chatbot system with LLM abstraction,
    intelligent conversation management, and a flexible character system.
    All processing happens locally on your device for complete privacy.
    """
    # Handle version flag
    if version:
        console.print("MYTHIC-LITE", style="bold magenta")
        console.print("v1.0.0", style="cyan")
        sys.exit(0)
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Setup logging with debug mode if enabled
    if debug:
        logger = setup_logging("mythic-cli", create_debug_config())
        console.print("Debug mode enabled - verbose logging active", style="bold yellow")
    else:
        logger = setup_logging("mythic-cli", None)
    
    ctx.obj['logger'] = logger
    
    # If no command specified, run setup then start in voice mode
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("Starting Mythic-Lite...", style="green")
        console.print("No command specified - running setup then starting voice mode", style="cyan")
        
        try:
            # First run initialization
            console.print("\nInitializing Mythic System", style="bold cyan")
            
            # Create orchestrator with debug config if enabled
            debug_config = create_debug_config() if debug else None
            orchestrator = create_orchestrator(debug_config)
            
            if initialize_system(orchestrator):
                # Show status
                show_system_status(orchestrator)
                
                # Now start in voice mode
                console.print("\nStarting voice conversation mode...", style="bold cyan")
                console.print("Launching Mythic in voice mode...", style="green")
                console.print("Starting voice conversation...", style="cyan")
                
                # Start the actual voice interface
                orchestrator.run_voice_mode()
                
            else:
                console.print("Failed to initialize Mythic system", style="bold red")
                console.print("Try using 'mythic init' to troubleshoot", style="cyan")
                sys.exit(1)
                        
        except KeyboardInterrupt:
            console.print("\nVoice mode interrupted - Mythic returns to the shadows...", style="yellow")
        except Exception as e:
            console.print(f"Failed to start voice mode: {e}", style="red")
            console.print("Try using a specific command like 'mythic voice' or 'mythic help'", style="cyan")
            sys.exit(1)
        finally:
            if 'orchestrator' in locals():
                orchestrator.cleanup()


# Add all commands to the CLI group
cli.add_command(chat)
cli.add_command(voice)
cli.add_command(init)
cli.add_command(config)
cli.add_command(status)
cli.add_command(benchmark)
cli.add_command(help)
cli.add_command(test_tts)


if __name__ == "__main__":
    cli()
