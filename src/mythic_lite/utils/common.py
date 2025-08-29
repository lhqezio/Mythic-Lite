"""
Common utilities for Mythic-Lite chatbot system.

Provides shared functionality used across multiple modules.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Any, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

console = Console()


def confirm_action(prompt: str, default: bool = True) -> bool:
    """Confirm an action with the user."""
    try:
        response = input(f"{prompt} ({'Y/n' if default else 'y/N'}): ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
        
    except (EOFError, KeyboardInterrupt):
        return False


def get_safe_input(prompt: str, default: str = "") -> str:
    """Get safe user input with error handling."""
    try:
        response = input(prompt).strip()
        return response if response else default
        
    except (EOFError, KeyboardInterrupt):
        return default


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size}B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f}KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f}MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.1f}GB"


def ensure_directory(path: str) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_project_root() -> Path:
    """Get the project root directory."""
    current_file = Path(__file__)
    return current_file.parent.parent.parent


def get_models_directory() -> Path:
    """Get the models directory path."""
    project_root = get_project_root()
    return project_root / "models"


def get_logs_directory() -> Path:
    """Get the logs directory path."""
    project_root = get_project_root()
    return project_root / "logs"


def create_status_table(title: str, data: Dict[str, Any]) -> Table:
    """Create a status table for display."""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        border_style="cyan"
    )
    table.add_column("Component", style="cyan bold", width=25)
    table.add_column("Status", style="white", width=15)
    table.add_column("Details", style="white")
    
    for component, info in data.items():
        if isinstance(info, dict):
            status = info.get('status', 'unknown')
            details = info.get('details', '')
        else:
            status = str(info)
            details = ''
        
        # Color-code status
        if status in ['active', 'success', 'true', 'enabled']:
            status_style = "green"
        elif status in ['inactive', 'failed', 'false', 'disabled']:
            status_style = "red"
        elif status in ['warning', 'partial']:
            status_style = "yellow"
        else:
            status_style = "white"
        
        table.add_row(component, status, details)
    
    return table


def create_info_panel(title: str, content: str, style: str = "cyan") -> Panel:
    """Create an info panel for display."""
    return Panel(
        content,
        title=title,
        border_style=style,
        box=ROUNDED
    )


def print_section_header(title: str, style: str = "bold cyan"):
    """Print a section header."""
    console.print(f"\n{title}", style=style)
    console.print("=" * len(title), style=style)


def print_subsection_header(title: str, style: str = "bold yellow"):
    """Print a subsection header."""
    console.print(f"\n{title}", style=style)
    console.print("-" * len(title), style=style)


def print_success(message: str):
    """Print a success message."""
    console.print(f"✓ {message}", style="bold green")


def print_error(message: str):
    """Print an error message."""
    console.print(f"✗ {message}", style="bold red")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"⚠ {message}", style="bold yellow")


def print_info(message: str):
    """Print an info message."""
    console.print(f"ℹ {message}", style="bold blue")


def print_progress(current: int, total: int, description: str = ""):
    """Print a progress bar."""
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 30
    filled_length = int(bar_length * current // total)
    
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    progress_text = f"{description} [{bar}] {percentage:.1f}% ({current}/{total})"
    console.print(progress_text, style="cyan")


def wait_with_progress(duration: float, description: str = "Waiting"):
    """Wait for a duration with a progress bar."""
    start_time = time.time()
    steps = 50
    
    for i in range(steps + 1):
        elapsed = time.time() - start_time
        progress = min(i / steps, 1.0)
        
        # Clear line and print progress
        console.print(f"\r{description} [{('█' * int(progress * 50)).ljust(50, '░')}] {progress*100:.1f}%", end="")
        
        if elapsed >= duration:
            break
        
        time.sleep(duration / steps)
    
    console.print()  # New line after progress


def get_system_info() -> Dict[str, Any]:
    """Get basic system information."""
    import platform
    
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'python_version': sys.version,
        'python_executable': sys.executable
    }


def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are available."""
    dependencies = {
        'llama_cpp': False,
        'piper_tts': False,
        'vosk': False,
        'pyaudio': False,
        'numpy': False,
        'rich': False,
        'click': False
    }
    
    try:
        import llama_cpp
        dependencies['llama_cpp'] = True
    except ImportError:
        pass
    
    try:
        import piper
        dependencies['piper_tts'] = True
    except ImportError:
        pass
    
    try:
        import vosk
        dependencies['vosk'] = True
    except ImportError:
        pass
    
    try:
        import pyaudio
        dependencies['pyaudio'] = True
    except ImportError:
        pass
    
    try:
        import numpy
        dependencies['numpy'] = True
    except ImportError:
        pass
    
    try:
        import rich
        dependencies['rich'] = True
    except ImportError:
        pass
    
    try:
        import click
        dependencies['click'] = True
    except ImportError:
        pass
    
    return dependencies


def validate_environment() -> Dict[str, Any]:
    """Validate the current environment."""
    validation = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'dependencies': check_dependencies(),
        'system_info': get_system_info()
    }
    
    # Check dependencies
    missing_deps = [dep for dep, available in validation['dependencies'].items() if not available]
    if missing_deps:
        validation['warnings'].append(f"Missing dependencies: {', '.join(missing_deps)}")
    
    # Check directories
    models_dir = get_models_directory()
    logs_dir = get_logs_directory()
    
    if not models_dir.exists():
        validation['warnings'].append("Models directory does not exist")
    
    if not logs_dir.exists():
        validation['warnings'].append("Logs directory does not exist")
    
    # Check permissions
    try:
        if not os.access(models_dir, os.W_OK):
            validation['errors'].append("No write access to models directory")
            validation['valid'] = False
    except Exception:
        validation['errors'].append("Cannot access models directory")
        validation['valid'] = False
    
    return validation