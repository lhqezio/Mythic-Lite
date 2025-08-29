#!/usr/bin/env python3
"""
Simple demo script for Mythic-Lite character system.

This script demonstrates how to use different characters
including the Mythic character as a demo.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mythic_lite.core import (
    ChatbotOrchestrator,
    create_mythic_demo_config,
    create_generic_config,
    get_character_manager
)


def main():
    """Run a simple character demo."""
    print("🎭 Mythic-Lite Character Demo")
    print("=" * 40)
    
    # Show available characters
    character_manager = get_character_manager()
    print(f"Available characters: {', '.join(character_manager.list_characters())}")
    
    # Demo 1: Mythic character
    print("\n🤖 Demo 1: Mythic Character")
    print("-" * 30)
    
    try:
        config = create_mythic_demo_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if orchestrator.initialize_workers():
            # Get character info
            character = character_manager.get_character("mythic")
            if character:
                print(f"Character: {character.personality.name}")
                print(f"Description: {character.personality.description}")
            
            # Simple conversation
            response = orchestrator.process_user_input("Hello! Tell me about yourself.")
            print(f"Response: {response}")
            
            orchestrator.cleanup()
            print("✅ Mythic demo completed")
        else:
            print("❌ Failed to initialize system")
    
    except Exception as e:
        print(f"❌ Mythic demo failed: {e}")
    
    # Demo 2: Generic assistant
    print("\n🤖 Demo 2: Generic Assistant")
    print("-" * 30)
    
    try:
        config = create_generic_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if orchestrator.initialize_workers():
            # Simple conversation
            response = orchestrator.process_user_input("Hello! Can you help me with a task?")
            print(f"Response: {response}")
            
            orchestrator.cleanup()
            print("✅ Generic assistant demo completed")
        else:
            print("❌ Failed to initialize system")
    
    except Exception as e:
        print(f"❌ Generic assistant demo failed: {e}")
    
    print("\n🎉 Demo completed!")
    print("\nTo run the full character demo with more features:")
    print("python examples/character_demo.py")


if __name__ == "__main__":
    main()