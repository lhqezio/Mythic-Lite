#!/usr/bin/env python3
"""
Simple entry point script for Mythic-Lite.
This script can be run directly to start the chatbot.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point."""
    try:
        from mythic_lite.utils.cli import cli
        
        # Start the CLI which will automatically run setup then start in voice mode
        # since no command is specified
        cli()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Mythic-Lite: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()