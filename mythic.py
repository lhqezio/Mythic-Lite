#!/usr/bin/env python3
"""
Main entry point for Mythic-Lite AI Chatbot
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from mythic_lite.utils.cli import cli
    cli()
except ImportError as e:
    print(f"Error importing Mythic-Lite: {e}")
    print("Please ensure all dependencies are installed and the project structure is correct.")
    sys.exit(1)
except Exception as e:
    print(f"Fatal error: {e}")
    sys.exit(1)