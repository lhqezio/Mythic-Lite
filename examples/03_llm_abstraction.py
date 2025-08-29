#!/usr/bin/env python3
"""
LLM Abstraction Example for Mythic-Lite

This example demonstrates how to use the LLM abstraction layer,
including different model types and configurations.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite.core import (
    ChatbotOrchestrator,
    create_generic_config,
    LLMConfig,
    ModelType
)
from mythic_lite.core.llm import LLMFactory


def demo_llm_factory():
    """Demonstrate the LLM factory functionality."""
    print("🔧 LLM Factory Demo")
    print("-" * 40)
    
    try:
        # Get the LLM factory
        factory = LLMFactory()
        
        # List available model types
        print("📋 Available Model Types:")
        for model_type in ModelType:
            print(f"  - {model_type.value}")
        
        # Get supported model types
        supported_types = factory.get_supported_model_types()
        print(f"\n✅ Supported Model Types: {supported_types}")
        
        # List available models
        available_models = factory.list_available_models()
        print(f"\n📦 Available Models: {available_models}")
        
        # Test model creation
        print("\n🧪 Testing Model Creation:")
        
        # Test LLaMA CPP model creation
        try:
            llama_config = LLMConfig(
                model_type=ModelType.LLAMA_CPP,
                model_path="models/llama-2-7b.gguf",  # Example path
                max_tokens=100,
                temperature=0.7
            )
            
            # Validate configuration
            validation_result = factory.validate_model_config(llama_config)
            print(f"  LLaMA CPP Config Valid: {validation_result['valid']}")
            if not validation_result['valid']:
                print(f"    Issues: {validation_result['issues']}")
            
        except Exception as e:
            print(f"  LLaMA CPP Test Failed: {e}")
        
        # Test OpenAI model creation (if available)
        try:
            openai_config = LLMConfig(
                model_type=ModelType.OPENAI,
                model_name="gpt-3.5-turbo",
                max_tokens=100,
                temperature=0.7
            )
            
            validation_result = factory.validate_model_config(openai_config)
            print(f"  OpenAI Config Valid: {validation_result['valid']}")
            if not validation_result['valid']:
                print(f"    Issues: {validation_result['issues']}")
                
        except Exception as e:
            print(f"  OpenAI Test Failed: {e}")
        
        print("✅ LLM Factory demo completed")
        return True
        
    except Exception as e:
        print(f"❌ LLM Factory demo failed: {e}")
        return False


def demo_custom_llm_config():
    """Demonstrate custom LLM configuration."""
    print("\n⚙️ Custom LLM Configuration Demo")
    print("-" * 40)
    
    try:
        # Create a custom configuration
        config = create_generic_config()
        
        # Customize LLM settings
        config.llm = LLMConfig(
            model_type=ModelType.LLAMA_CPP,
            model_path="models/llama-2-7b.gguf",  # Example path
            max_tokens=200,
            temperature=0.8,
            context_window=4096,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1
        )
        
        # Initialize orchestrator with custom config
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized with custom LLM configuration")
        
        # Get LLM worker info
        llm_worker = orchestrator.llm_worker
        if llm_worker and llm_worker.llm_model:
            model_info = llm_worker.llm_model.get_model_info()
            print(f"📊 Model Info: {model_info}")
        
        # Test conversation with custom settings
        print("\n💬 Testing conversation with custom settings...")
        response = orchestrator.process_user_input("Hello! How are you today?")
        print(f"🤖 Response: {response}")
        
        # Get performance stats
        stats = orchestrator.get_performance_stats()
        print(f"\n📈 Performance Stats:")
        print(f"  Average Response Time: {stats['average_response_time']:.2f}s")
        print(f"  Total Tokens Generated: {stats['total_tokens_generated']}")
        
        orchestrator.cleanup()
        print("✅ Custom LLM configuration demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Custom LLM configuration demo failed: {e}")
        return False


def demo_streaming_response():
    """Demonstrate streaming response functionality."""
    print("\n🌊 Streaming Response Demo")
    print("-" * 40)
    
    try:
        # Create configuration with streaming enabled
        config = create_generic_config()
        config.conversation.enable_streaming = True
        
        orchestrator = ChatbotOrchestrator(config)
        
        if not orchestrator.initialize_workers():
            print("❌ Failed to initialize system")
            return False
        
        print("✅ System initialized with streaming enabled")
        
        # Test streaming response
        print("\n💬 Testing streaming response...")
        print("🤖 Assistant: ", end="", flush=True)
        
        for token in orchestrator.process_user_input_stream("Tell me a short story about a robot"):
            print(token, end="", flush=True)
        
        print("\n\n✅ Streaming response demo completed")
        
        orchestrator.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Streaming response demo failed: {e}")
        return False


def main():
    """Run all LLM abstraction demos."""
    print("🔧 Mythic-Lite LLM Abstraction Example")
    print("=" * 60)
    
    # Run demos
    demos = [
        ("LLM Factory", demo_llm_factory),
        ("Custom LLM Configuration", demo_custom_llm_config),
        ("Streaming Response", demo_streaming_response)
    ]
    
    successful_demos = 0
    total_demos = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*60}")
        if demo_func():
            successful_demos += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 LLM abstraction example completed!")
    print(f"✅ Successful demos: {successful_demos}/{total_demos}")
    
    if successful_demos == total_demos:
        print("🎊 All demos completed successfully!")
    else:
        print("⚠️ Some demos failed. Check your configuration and model files.")


if __name__ == "__main__":
    main()