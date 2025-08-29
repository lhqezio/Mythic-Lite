#!/usr/bin/env python3
"""
Memory System Example for Mythic-Lite

This example demonstrates how to use the memory system,
including conversation memory, summarization, and recall.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite.core import (
    ChatbotOrchestrator,
    create_generic_config
)


def demo_memory_basic():
    """Demonstrate basic memory functionality."""
    print("🧠 Basic Memory Demo")
    print("-" * 40)
    
    try:
        # Create configuration with memory enabled
        config = create_generic_config()
        config.memory.enable_memory = True
        config.memory.max_memories = 50
        
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized with memory enabled")
        
        # Get memory worker
        memory_worker = orchestrator.memory_worker
        if not memory_worker:
            print("❌ Memory worker not available")
            return False
        
        # Store some memories
        print("\n💾 Storing memories...")
        
        memories = [
            ("user", "My name is Alice", "assistant", "Nice to meet you, Alice!"),
            ("user", "I work as a software engineer", "assistant", "That's interesting! What kind of software do you work on?"),
            ("user", "I like to read science fiction books", "assistant", "Science fiction is a great genre! Any favorite authors?"),
            ("user", "I'm learning Python programming", "assistant", "Python is an excellent language to learn! How's it going?")
        ]
        
        for user_msg, assistant_msg in memories:
            memory_worker.store_conversation_memory(user_msg, assistant_msg, {})
            print(f"  Stored: {user_msg[:30]}...")
        
        # Recall memories
        print("\n🔍 Recalling memories...")
        
        queries = [
            "What do you know about Alice?",
            "Tell me about Alice's work",
            "What are Alice's interests?",
            "What is Alice learning?"
        ]
        
        for query in queries:
            relevant_memories = memory_worker.recall_relevant_memory(query)
            print(f"\nQuery: {query}")
            print(f"Relevant memories: {len(relevant_memories)} found")
            for memory in relevant_memories[:2]:  # Show first 2
                print(f"  - {memory.get('summary', 'No summary')}")
        
        # Get memory statistics
        stats = memory_worker.get_performance_stats()
        print(f"\n📊 Memory Statistics:")
        print(f"  Total memories stored: {stats['total_memories_stored']}")
        print(f"  Total memories recalled: {stats['total_memories_recalled']}")
        print(f"  Total summaries generated: {stats['total_summaries_generated']}")
        
        orchestrator.cleanup()
        print("✅ Basic memory demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Basic memory demo failed: {e}")
        return False


def demo_memory_conversation():
    """Demonstrate memory in conversation context."""
    print("\n💬 Memory in Conversation Demo")
    print("-" * 40)
    
    try:
        # Create configuration with memory enabled
        config = create_generic_config()
        config.memory.enable_memory = True
        config.memory.max_memories = 20
        
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized with memory enabled")
        
        # Simulate a conversation with memory
        conversation = [
            ("Hello! My name is Bob.", "Hello Bob! Nice to meet you. How can I help you today?"),
            ("I'm a teacher and I love hiking.", "That's wonderful! Teaching and hiking are both great activities. What do you teach?"),
            ("I teach mathematics to high school students.", "That's a challenging but rewarding job! Do you find that your students enjoy math?"),
            ("Some do, but many struggle with it.", "That's common with math. What strategies do you use to help struggling students?"),
            ("I try to make it more practical and relatable.", "That's a great approach! Real-world applications can really help students understand abstract concepts.")
        ]
        
        print("\n💬 Simulating conversation with memory...")
        
        for i, (user_msg, expected_response) in enumerate(conversation, 1):
            print(f"\n--- Turn {i} ---")
            print(f"👤 Bob: {user_msg}")
            print(f"🤖 Assistant: {expected_response}")
            
            # Process the message (this will automatically store in memory)
            response = orchestrator.process_user_input(user_msg)
            print(f"🤖 Actual Response: {response}")
        
        # Test memory recall
        print("\n🔍 Testing memory recall...")
        
        recall_queries = [
            "What do you know about Bob?",
            "What does Bob do for work?",
            "What are Bob's interests?",
            "What challenges does Bob face in his work?"
        ]
        
        for query in recall_queries:
            print(f"\nQuery: {query}")
            # This would normally be done through the conversation worker
            # For demo purposes, we'll simulate it
            print("  (Memory recall would happen automatically in conversation)")
        
        orchestrator.cleanup()
        print("✅ Memory in conversation demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Memory in conversation demo failed: {e}")
        return False


def demo_memory_management():
    """Demonstrate memory management features."""
    print("\n🗂️ Memory Management Demo")
    print("-" * 40)
    
    try:
        # Create configuration with memory enabled
        config = create_generic_config()
        config.memory.enable_memory = True
        config.memory.max_memories = 10
        config.memory.memory_ttl_hours = 1  # Short TTL for demo
        
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized with memory management")
        
        memory_worker = orchestrator.memory_worker
        
        # Store some test memories
        print("\n💾 Storing test memories...")
        for i in range(5):
            memory_worker.store_conversation_memory(
                f"Test message {i}",
                f"Test response {i}",
                {"test": True, "index": i}
            )
        
        # Export memory
        print("\n📤 Exporting memory...")
        try:
            exported_memory = memory_worker.export_memory()
            print(f"  Exported {len(exported_memory)} memories")
        except Exception as e:
            print(f"  Export failed: {e}")
        
        # Get memory statistics
        print("\n📊 Memory Statistics:")
        stats = memory_worker.get_performance_stats()
        print(f"  Total memories stored: {stats['total_memories_stored']}")
        print(f"  Memory TTL: {config.memory.memory_ttl_hours} hours")
        print(f"  Max memories: {config.memory.max_memories}")
        
        # Clear memory
        print("\n🗑️ Clearing memory...")
        try:
            memory_worker.clear_memory()
            print("  Memory cleared successfully")
        except Exception as e:
            print(f"  Clear failed: {e}")
        
        # Health check
        print("\n🏥 Memory health check...")
        health = memory_worker.health_check()
        print(f"  Health status: {health['status']}")
        print(f"  Memory count: {health['memory_count']}")
        print(f"  Last activity: {health['last_activity']}")
        
        orchestrator.cleanup()
        print("✅ Memory management demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Memory management demo failed: {e}")
        return False


def main():
    """Run all memory system demos."""
    print("🧠 Mythic-Lite Memory System Example")
    print("=" * 60)
    
    # Run demos
    demos = [
        ("Basic Memory", demo_memory_basic),
        ("Memory in Conversation", demo_memory_conversation),
        ("Memory Management", demo_memory_management)
    ]
    
    successful_demos = 0
    total_demos = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*60}")
        if demo_func():
            successful_demos += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 Memory system example completed!")
    print(f"✅ Successful demos: {successful_demos}/{total_demos}")
    
    if successful_demos == total_demos:
        print("🎊 All demos completed successfully!")
    else:
        print("⚠️ Some demos failed. Check your configuration and model files.")


if __name__ == "__main__":
    main()