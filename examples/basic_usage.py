#!/usr/bin/env python3
"""
Basic usage example for Mythic-Lite AI chatbot system.

This example demonstrates how to:
1. Initialize the chatbot system
2. Start a conversation
3. Process text input
4. Handle voice input/output
5. Manage conversation memory
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite import (
    ChatbotOrchestrator,
    Config,
    Logger
)


async def main():
    """Main example function."""
    print("🤖 Mythic-Lite Basic Usage Example")
    print("=" * 50)
    
    # Initialize configuration
    config = Config()
    config.log_level = logging.INFO
    
    # Initialize logger
    logger = Logger(config)
    logger.info("Starting Mythic-Lite example...")
    
    try:
        # Initialize chatbot orchestrator
        print("🚀 Initializing chatbot system...")
        orchestrator = ChatbotOrchestrator(config, logger)
        
        # Wait for system to be ready
        await orchestrator.initialize()
        print("✅ System initialized successfully!")
        
        # Example conversation
        print("\n💬 Starting conversation...")
        print("Type 'quit' to exit, 'voice' to toggle voice mode")
        
        voice_mode = False
        
        while True:
            try:
                # Get user input
                if voice_mode:
                    print("\n🎤 Listening... (speak now)")
                    user_input = await orchestrator.listen_for_speech()
                    if user_input:
                        print(f"🎤 You said: {user_input}")
                    else:
                        print("🎤 No speech detected, please try again")
                        continue
                else:
                    user_input = input("\n💬 You: ").strip()
                
                # Check for commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for chatting with Mythic!")
                    break
                elif user_input.lower() == 'voice':
                    voice_mode = not voice_mode
                    mode = "ON" if voice_mode else "OFF"
                    print(f"🎤 Voice mode: {mode}")
                    continue
                elif not user_input:
                    continue
                
                # Process user input and get response
                print("🤔 Processing...")
                response = await orchestrator.process_input(user_input)
                
                # Display response
                print(f"🤖 Mythic: {response}")
                
                # Speak response if in voice mode
                if voice_mode:
                    print("🔊 Speaking response...")
                    await orchestrator.speak_text(response)
                
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}")
                print(f"❌ Error: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        print(f"❌ Failed to initialize: {e}")
        return 1
    
    finally:
        # Cleanup
        if 'orchestrator' in locals():
            await orchestrator.cleanup()
        logger.info("Example completed")
    
    return 0


def run_example():
    """Run the example with proper error handling."""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_example()
    sys.exit(exit_code)