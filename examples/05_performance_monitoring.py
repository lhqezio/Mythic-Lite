#!/usr/bin/env python3
"""
Performance Monitoring Example for Mythic-Lite

This example demonstrates how to use the performance monitoring
and health check features of the system.
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite.core import (
    ChatbotOrchestrator,
    create_generic_config
)


def demo_system_health():
    """Demonstrate system health monitoring."""
    print("🏥 System Health Monitoring Demo")
    print("-" * 40)
    
    try:
        # Create configuration
        config = create_generic_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized successfully")
        
        # Get system health
        print("\n🔍 Checking system health...")
        health = orchestrator.get_system_health()
        
        print(f"📊 Overall Status: {health['overall_status']}")
        print(f"🔧 LLM Worker: {health['llm_worker']['status']}")
        print(f"🧠 Memory Worker: {health['memory_worker']['status']}")
        print(f"💬 Conversation Worker: {health['conversation_worker']['status']}")
        
        # Show detailed health info
        print("\n📋 Detailed Health Information:")
        for worker_name, worker_health in health.items():
            if worker_name != 'overall_status':
                print(f"\n{worker_name.upper()}:")
                for key, value in worker_health.items():
                    if key != 'status':
                        print(f"  {key}: {value}")
        
        orchestrator.cleanup()
        print("✅ System health demo completed")
        return True
        
    except Exception as e:
        print(f"❌ System health demo failed: {e}")
        return False


def demo_performance_tracking():
    """Demonstrate performance tracking."""
    print("\n📈 Performance Tracking Demo")
    print("-" * 40)
    
    try:
        # Create configuration
        config = create_generic_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized successfully")
        
        # Run some conversations to generate performance data
        print("\n💬 Running conversations for performance tracking...")
        
        test_messages = [
            "Hello! How are you today?",
            "Can you tell me a short story?",
            "What's the weather like?",
            "How does machine learning work?",
            "Thank you for your help!"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Conversation {i} ---")
            start_time = time.time()
            
            response = orchestrator.process_user_input(message)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"Message: {message}")
            print(f"Response: {response[:50]}...")
            print(f"Response Time: {response_time:.2f}s")
        
        # Get performance statistics
        print("\n📊 Performance Statistics:")
        stats = orchestrator.get_performance_stats()
        
        print(f"Total Conversations: {stats['total_conversations']}")
        print(f"Average Response Time: {stats['average_response_time']:.2f}s")
        print(f"Total Tokens Generated: {stats['total_tokens_generated']}")
        print(f"Total Response Time: {stats['total_response_time']:.2f}s")
        
        if 'tokens_per_second' in stats:
            print(f"Tokens per Second: {stats['tokens_per_second']:.2f}")
        
        if 'uptime_hours' in stats:
            print(f"Uptime: {stats['uptime_hours']:.2f} hours")
        
        orchestrator.cleanup()
        print("✅ Performance tracking demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Performance tracking demo failed: {e}")
        return False


def demo_worker_status():
    """Demonstrate individual worker status monitoring."""
    print("\n🔧 Worker Status Monitoring Demo")
    print("-" * 40)
    
    try:
        # Create configuration
        config = create_generic_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized successfully")
        
        # Get worker status
        print("\n📋 Worker Status:")
        worker_status = orchestrator.get_worker_status()
        
        for worker_name, status in worker_status.items():
            print(f"\n{worker_name.upper()}:")
            print(f"  Status: {status['status']}")
            print(f"  Initialized: {status['initialized']}")
            print(f"  Last Activity: {status['last_activity']}")
            
            if 'performance' in status:
                perf = status['performance']
                print(f"  Performance:")
                for key, value in perf.items():
                    print(f"    {key}: {value}")
        
        orchestrator.cleanup()
        print("✅ Worker status demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Worker status demo failed: {e}")
        return False


def demo_benchmark():
    """Demonstrate benchmarking functionality."""
    print("\n🏃 Benchmark Demo")
    print("-" * 40)
    
    try:
        # Create configuration
        config = create_generic_config()
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized successfully")
        
        # Run benchmark
        print("\n🏃 Running benchmark...")
        benchmark_result = orchestrator.run_benchmark()
        
        print(f"📊 Benchmark Results:")
        print(f"  Response Time: {benchmark_result['response_time']:.2f}s")
        print(f"  Tokens Generated: {benchmark_result['tokens_generated']}")
        print(f"  Tokens per Second: {benchmark_result['tokens_per_second']:.2f}")
        print(f"  Memory Usage: {benchmark_result.get('memory_usage', 'N/A')}")
        
        # Performance rating
        response_time = benchmark_result['response_time']
        if response_time < 1.0:
            rating = "Excellent"
        elif response_time < 3.0:
            rating = "Good"
        elif response_time < 5.0:
            rating = "Fair"
        else:
            rating = "Slow"
        
        print(f"  Performance Rating: {rating}")
        
        orchestrator.cleanup()
        print("✅ Benchmark demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Benchmark demo failed: {e}")
        return False


def main():
    """Run all performance monitoring demos."""
    print("📊 Mythic-Lite Performance Monitoring Example")
    print("=" * 60)
    
    # Run demos
    demos = [
        ("System Health", demo_system_health),
        ("Performance Tracking", demo_performance_tracking),
        ("Worker Status", demo_worker_status),
        ("Benchmark", demo_benchmark)
    ]
    
    successful_demos = 0
    total_demos = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*60}")
        if demo_func():
            successful_demos += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 Performance monitoring example completed!")
    print(f"✅ Successful demos: {successful_demos}/{total_demos}")
    
    if successful_demos == total_demos:
        print("🎊 All demos completed successfully!")
    else:
        print("⚠️ Some demos failed. Check your configuration and model files.")


if __name__ == "__main__":
    main()