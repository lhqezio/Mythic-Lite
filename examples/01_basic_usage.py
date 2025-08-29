#!/usr/bin/env python3
"""
Basic Usage Example for Mythic-Lite

This example demonstrates the fundamental usage of the Mythic-Lite
chatbot system with a generic AI assistant.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite.core import ChatbotOrchestrator, create_generic_config


def main():
    """Demonstrate basic usage of Mythic-Lite."""
    print("🤖 Mythic-Lite Basic Usage Example")
    print("=" * 50)
    
    try:
        # Create a generic configuration
        config = create_generic_config()
        
        # Initialize the orchestrator
        orchestrator = ChatbotOrchestrator(config)
        
        print("🔄 Initializing system...")
        
        # Initialize all workers
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return
        
        print("✅ System initialized successfully!")
        
        # Get system status
        status = orchestrator.get_system_status()
        print(f"📊 System Status: {status['overall_status']}")
        print(f"🔧 LLM Worker: {status['llm_worker']}")
        print(f"🧠 Memory Worker: {status['memory_worker']}")
        print(f"💬 Conversation Worker: {status['conversation_worker']}")
        
        # Start a simple conversation
        print("\n💬 Starting conversation...")
        print("-" * 30)
        
        # Example conversation
        messages = [
            "Hello! Can you help me with a task?",
            "What's the weather like today?",
            "Can you explain how machine learning works?",
            "Thank you for your help!"
        ]
        
        for message in messages:
            print(f"\n👤 You: {message}")
            
            # Process the message
            response = orchestrator.process_user_input(message)
            print(f"🤖 Assistant: {response}")
        
        # Get performance statistics
        print("\n📈 Performance Statistics")
        print("-" * 30)
        stats = orchestrator.get_performance_stats()
        print(f"Total Conversations: {stats['total_conversations']}")
        print(f"Average Response Time: {stats['average_response_time']:.2f}s")
        print(f"Total Tokens Generated: {stats['total_tokens_generated']}")
        
        # Cleanup
        orchestrator.cleanup()
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()