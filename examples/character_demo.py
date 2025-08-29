"""
Demo example for Mythic-Lite character system.

Shows how to use the character system with different characters,
including the Mythic character as a demo.
"""

from mythic_lite.core import (
    ChatbotOrchestrator,
    create_mythic_demo_config,
    create_generic_config,
    create_custom_character_config,
    create_custom_character,
    get_character_manager
)


def demo_mythic_character():
    """Demo the Mythic character."""
    print("🤖 Mythic Character Demo")
    print("=" * 50)
    
    # Create demo configuration with Mythic character
    config = create_mythic_demo_config()
    orchestrator = ChatbotOrchestrator(config)
    
    # Initialize the system
    if orchestrator.initialize_workers():
        print("✅ System initialized with Mythic character")
        
        # Get character info
        character = get_character_manager().get_character("mythic")
        if character:
            print(f"Character: {character.personality.name}")
            print(f"Description: {character.personality.description}")
            print(f"Personality: {', '.join(character.personality.personality_traits[:3])}...")
        
        # Demo conversation
        print("\n💬 Starting conversation with Mythic...")
        response = orchestrator.process_user_input("Hello! Tell me about yourself.")
        print(f"Mythic: {response}")
        
        # Cleanup
        orchestrator.cleanup()
        print("\n✅ Mythic character demo completed")
    else:
        print("❌ Failed to initialize system")


def demo_generic_assistant():
    """Demo the generic assistant without character."""
    print("\n🤖 Generic Assistant Demo")
    print("=" * 50)
    
    # Create generic configuration
    config = create_generic_config()
    orchestrator = ChatbotOrchestrator(config)
    
    # Initialize the system
    if orchestrator.initialize_workers():
        print("✅ System initialized with generic assistant")
        
        # Demo conversation
        print("\n💬 Starting conversation with generic assistant...")
        response = orchestrator.process_user_input("Hello! Can you help me with a task?")
        print(f"Assistant: {response}")
        
        # Cleanup
        orchestrator.cleanup()
        print("\n✅ Generic assistant demo completed")
    else:
        print("❌ Failed to initialize system")


def demo_custom_character():
    """Demo a custom character."""
    print("\n🤖 Custom Character Demo")
    print("=" * 50)
    
    # Create a custom character
    character_manager = get_character_manager()
    custom_character = character_manager.create_custom_character(
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
    
    # Add the custom character
    character_manager.add_character("sage", custom_character)
    
    # Create configuration with custom character
    config = create_custom_character_config("sage")
    orchestrator = ChatbotOrchestrator(config)
    
    # Initialize the system
    if orchestrator.initialize_workers():
        print("✅ System initialized with custom Sage character")
        
        # Get character info
        character = character_manager.get_character("sage")
        if character:
            print(f"Character: {character.personality.name}")
            print(f"Description: {character.personality.description}")
            print(f"Personality: {', '.join(character.personality.personality_traits[:3])}...")
        
        # Demo conversation
        print("\n💬 Starting conversation with Sage...")
        response = orchestrator.process_user_input("What is the meaning of life?")
        print(f"Sage: {response}")
        
        # Cleanup
        orchestrator.cleanup()
        print("\n✅ Custom character demo completed")
    else:
        print("❌ Failed to initialize system")


def demo_character_comparison():
    """Demo comparing different characters."""
    print("\n🤖 Character Comparison Demo")
    print("=" * 50)
    
    # Test different characters with the same question
    question = "What's your approach to solving problems?"
    
    characters = [
        ("mythic", "Mythic (Mercenary)"),
        ("sage", "Sage (Philosopher)"),
        (None, "Generic Assistant")
    ]
    
    for character_name, character_label in characters:
        print(f"\n--- {character_label} ---")
        
        if character_name:
            config = create_custom_character_config(character_name)
        else:
            config = create_generic_config()
        
        orchestrator = ChatbotOrchestrator(config)
        
        if orchestrator.initialize_workers():
            response = orchestrator.process_user_input(question)
            print(f"Response: {response[:100]}...")
            orchestrator.cleanup()
        else:
            print("Failed to initialize")


def main():
    """Run all character demos."""
    print("🎭 Mythic-Lite Character System Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Mythic character
        demo_mythic_character()
        
        # Demo 2: Generic assistant
        demo_generic_assistant()
        
        # Demo 3: Custom character
        demo_custom_character()
        
        # Demo 4: Character comparison
        demo_character_comparison()
        
        print("\n🎉 All character demos completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    main()