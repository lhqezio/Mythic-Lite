#!/usr/bin/env python3
"""
TTS Example - How to use the Text-to-Speech Worker

This example shows how to:
1. Create and initialize a TTS worker
2. Generate speech from text
3. Play audio through speakers
4. Handle different voice options
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    """Main TTS example function."""
    print("🎤 TTS Example - Text-to-Speech with Piper")
    print("=" * 50)
    
    try:
        # Import the TTS worker
        from mythic_lite.workers.tts_worker import TTSWorker
        print("✅ TTS Worker imported successfully")
        
        # Create TTS worker with default config
        print("\n1. Creating TTS worker...")
        tts = TTSWorker()
        print("✅ TTS Worker created")
        
        # Show available voices
        print(f"\n2. Available voices:")
        for voice_name, voice_path in tts.config.tts.AVAILABLE_VOICES.items():
            print(f"   - {voice_name} -> {voice_path}")
        
        # Initialize TTS system
        print(f"\n3. Initializing TTS system...")
        print(f"   Voice: {tts.config.tts.voice_path}")
        print(f"   Sample rate: {tts.config.tts.sample_rate}Hz")
        print(f"   Channels: {tts.config.tts.channels}")
        
        if tts.initialize():
            print("✅ TTS initialized successfully!")
        else:
            print(f"❌ TTS initialization failed: {tts.initialization_error}")
            print("\n💡 Troubleshooting tips:")
            print("   - Make sure huggingface-hub is installed: pip install huggingface-hub")
            print("   - Check internet connection for model download")
            print("   - Verify the voice path is correct")
            return False
        
        # Test different text samples
        test_texts = [
            "Hello! This is a test of the text to speech system.",
            "The quick brown fox jumps over the lazy dog.",
            "Welcome to Mythic-Lite, your AI assistant.",
            "This voice is powered by Piper TTS technology."
        ]
        
        print(f"\n4. Testing speech generation...")
        for i, text in enumerate(test_texts, 1):
            print(f"\n   Test {i}: '{text}'")
            
            # Generate and play speech
            if tts.speak(text):
                print("   ✅ Audio queued for playback")
                
                # Wait for audio to finish (with timeout)
                start_time = time.time()
                while tts.has_audio_playing() and (time.time() - start_time) < 5.0:
                    time.sleep(0.1)
                
                print("   ✅ Audio playback completed")
            else:
                print("   ❌ Failed to generate speech")
        
        # Show performance stats
        print(f"\n5. Performance Statistics:")
        stats = tts.get_performance_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Cleanup
        print(f"\n6. Cleaning up...")
        tts.cleanup()
        print("✅ TTS worker cleaned up")
        
        print(f"\n🎉 TTS Example completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\n💡 Make sure to install dependencies:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)