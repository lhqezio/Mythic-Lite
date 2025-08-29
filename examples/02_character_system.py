#!/usr/bin/env python3
"""
Character System Example for Mythic-Lite

This example demonstrates how to use the character system,
including the built-in Mythic character and custom characters.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite.core import (
    ChatbotOrchestrator,
    create_mythic_demo_config,
    create_generic_config,
    create_custom_character_config,
    create_custom_character,
    get_character_manager
)


def demo_mythic_character():
    """Demonstrate the Mythic character."""
    print("🎭 Mythic Character Demo")
    print("-" * 40)
    
    try:
        # Create configuration with Mythic character
        config = create_mythic_demo_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        # Get character information
        character_manager = get_character_manager()
        character = character_manager.get_character("mythic")
        
        if character:
            print(f"🤖 Character: {character.personality.name}")
            print(f"📝 Description: {character.personality.description}")
            print(f"🎭 Personality: {', '.join(character.personality.personality_traits[:3])}...")
        
        # Example conversation
        messages = [
            "Hello! Tell me about yourself.",
            "What's your approach to solving problems?",
            "How do you handle difficult situations?",
            "Thank you for your time."
        ]
        
        for message in messages:
            print(f"\n👤 You: {message}")
            response = orchestrator.process_user_input(message)
            print(f"🤖 Mythic: {response}")
        
        orchestrator.cleanup()
        print("✅ Mythic character demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Mythic demo failed: {e}")
        return False


def demo_generic_assistant():
    """Demonstrate the generic assistant."""
    print("\n🤖 Generic Assistant Demo")
    print("-" * 40)
    
    try:
        # Create generic configuration
        config = create_generic_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("🤖 Using generic AI assistant")
        
        # Example conversation
        messages = [
            "Hello! Can you help me with a task?",
            "What's your approach to solving problems?",
            "How do you handle difficult situations?",
            "Thank you for your help."
        ]
        
        for message in messages:
            print(f"\n👤 You: {message}")
            response = orchestrator.process_user_input(message)
            print(f"🤖 Assistant: {response}")
        
        orchestrator.cleanup()
        print("✅ Generic assistant demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Generic assistant demo failed: {e}")
        return False


def demo_custom_character():
    """Demonstrate a custom character."""
    print("\n🎨 Custom Character Demo")
    print("-" * 40)
    
    try:
        # Create a custom character
        character_manager = get_character_manager()
        
        sage_character = character_manager.create_custom_character(
            name="Sage",
            description="A wise and philosophical AI mentor who speaks in metaphors and ancient wisdom",
            personality_traits=[
                "Wise and contemplative",
                "Philosophical and deep",
                "Patient and understanding",
                "Speaks in metaphors",
                "Values knowledge and growth"
            ],
            speech_patterns=[
                "Uses metaphors and analogies",
                "References ancient wisdom",
                "Speaks thoughtfully and deliberately",
                "Asks probing questions",
                "Shares philosophical insights"
            ],
            interests=[
                "Philosophy and wisdom",
                "Personal growth and development",
                "Understanding human nature",
                "Ancient knowledge and traditions",
                "Meaningful conversations"
            ],
            formality_level=8,
            humor_level=3,
            assertiveness=5,
            empathy_level=9,
            greeting_style="formal",
            farewell_style="formal",
            question_style="philosophical"
        )
        
        # Add the character to the manager
        character_manager.add_character("sage", sage_character)
        
        # Create configuration with custom character
        config = create_custom_character_config("sage")
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        # Get character information
        character = character_manager.get_character("sage")
        if character:
            print(f"🤖 Character: {character.personality.name}")
            print(f"📝 Description: {character.personality.description}")
            print(f"🎭 Personality: {', '.join(character.personality.personality_traits[:3])}...")
        
        # Example conversation
        messages = [
            "What is the meaning of life?",
            "How should I approach difficult decisions?",
            "What wisdom can you share about personal growth?",
            "Thank you for your wisdom."
        ]
        
        for message in messages:
            print(f"\n👤 You: {message}")
            response = orchestrator.process_user_input(message)
            print(f"🤖 Sage: {response}")
        
        orchestrator.cleanup()
        print("✅ Custom character demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Custom character demo failed: {e}")
        return False


def main():
    """Run all character demos."""
    print("🎭 Mythic-Lite Character System Example")
    print("=" * 60)
    
    # Show available characters
    character_manager = get_character_manager()
    print(f"📚 Available characters: {', '.join(character_manager.list_characters())}")
    
    # Run demos
    demos = [
        ("Mythic Character", demo_mythic_character),
        ("Generic Assistant", demo_generic_assistant),
        ("Custom Character", demo_custom_character)
    ]
    
    successful_demos = 0
    total_demos = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*60}")
        if demo_func():
            successful_demos += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 Character system example completed!")
    print(f"✅ Successful demos: {successful_demos}/{total_demos}")
    
    if successful_demos == total_demos:
        print("🎊 All demos completed successfully!")
    else:
        print("⚠️ Some demos failed. Check your configuration and model files.")


if __name__ == "__main__":
    main()