"""
Common utility functions for Mythic-Lite chatbot system.
Consolidates repeated operations and provides shared functionality.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Any, Callable
from rich.console import Console

console = Console()


def safe_input(prompt: str = "") -> str:
    """Safely get user input with proper error handling."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        console.print("\nInput interrupted", style="yellow")
        return "quit"
    except Exception as e:
        console.print(f"Input error: {e}", style="red")
        return "quit"


def safe_choice(prompt: str, valid_choices: list, default: Optional[str] = None) -> Optional[str]:
    """Safely get user choice from a list of valid options."""
    try:
        choice = input(prompt).strip().lower()
        if choice in valid_choices:
            return choice
        elif default and choice == "":
            return default
        else:
            console.print(f"Invalid choice. Valid options: {', '.join(valid_choices)}", style="yellow")
            return None
    except (EOFError, KeyboardInterrupt):
        console.print("\nChoice interrupted", style="yellow")
        return None
    except Exception as e:
        console.print(f"Choice error: {e}", style="red")
        return None


def confirm_action(prompt: str = "Continue? (y/n): ", default: bool = True) -> bool:
    """Get user confirmation for an action."""
    try:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes', '']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            console.print("Please enter 'y' or 'n'", style="yellow")
            return confirm_action(prompt, default)
    except (EOFError, KeyboardInterrupt):
        console.print("\nConfirmation interrupted", style="yellow")
        return False


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable format."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_file_size(bytes_size: int) -> str:
    """Format file size in a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}TB"


def ensure_directory(path: Path) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        console.print(f"Failed to create directory {path}: {e}", style="red")
        return False


def retry_operation(operation: Callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Retry an operation with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            console.print(f"Operation failed (attempt {attempt + 1}/{max_attempts}): {e}", style="yellow")
            time.sleep(delay * (2 ** attempt))
    
    raise RuntimeError(f"Operation failed after {max_attempts} attempts")


def validate_file_path(file_path: Path, required: bool = True) -> bool:
    """Validate that a file path exists and is accessible."""
    if not file_path.exists():
        if required:
            console.print(f"Required file not found: {file_path}", style="red")
            return False
        else:
            console.print(f"File not found: {file_path}", style="yellow")
            return False
    
    if not file_path.is_file():
        console.print(f"Path is not a file: {file_path}", style="red")
        return False
    
    if not file_path.is_readable():
        console.print(f"File is not readable: {file_path}", style="red")
        return False
    
    return True


def validate_directory_path(dir_path: Path, required: bool = True) -> bool:
    """Validate that a directory path exists and is accessible."""
    if not dir_path.exists():
        if required:
            console.print(f"Required directory not found: {dir_path}", style="red")
            return False
        else:
            console.print(f"Directory not found: {dir_path}", style="yellow")
            return False
    
    if not dir_path.is_dir():
        console.print(f"Path is not a directory: {dir_path}", style="red")
        return False
    
    if not dir_path.is_readable():
        console.print(f"Directory is not readable: {dir_path}", style="red")
        return False
    
    return True


def get_system_info() -> dict:
    """Get basic system information."""
    import platform
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation()
    }


def check_dependencies(required_packages: list) -> dict:
    """Check if required packages are available."""
    results = {}
    
    for package in required_packages:
        try:
            __import__(package)
            results[package] = {"available": True, "error": None}
        except ImportError as e:
            results[package] = {"available": False, "error": str(e)}
    
    return results


def print_separator(char: str = "=", length: int = 80):
    """Print a separator line."""
    console.print(char * length, style="dim white")


def print_section_header(title: str, char: str = "="):
    """Print a section header with separator."""
    print_separator(char)
    console.print(title, style="bold cyan")
    print_separator(char)