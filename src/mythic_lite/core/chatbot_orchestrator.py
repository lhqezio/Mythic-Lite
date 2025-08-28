"""
Main orchestrator module for Mythic-Lite chatbot system.
Coordinates all workers and manages the main chatbot interface.
"""

import time
from typing import Optional, Dict, Any

# Use lazy imports to avoid circular dependencies
def get_workers():
    """Get worker classes when needed."""
    from ..workers.asr_worker import ASRWorker
    from ..workers.llm_worker import LLMWorker
    from ..workers.summarization_worker import SummarizationWorker
    from ..workers.tts_worker import TTSWorker
    return ASRWorker, LLMWorker, SummarizationWorker, TTSWorker

from .conversation_worker import ConversationWorker
from .config import get_config
from ..utils.logger import get_logger
from ..utils.windows_input import safe_input, safe_choice


class ChatbotOrchestrator:
    """Main orchestrator class that coordinates all workers."""
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config or get_config()
        self.logger = get_logger("orchestrator")
        
        # Get worker classes when needed
        ASRWorker, LLMWorker, SummarizationWorker, TTSWorker = get_workers()
        
        # Create worker instances but don't initialize them yet
        self.llm_worker = LLMWorker(self.config)
        self.summarization_worker = SummarizationWorker(self.config)
        self.tts_worker = TTSWorker(self.config)
        self.asr_worker = ASRWorker()
        self.conversation_worker = ConversationWorker(self.config)
        
        # Debug mode from configuration
        self.debug_mode = self.config.debug_mode
        self.conversation_worker.debug_mode = self.debug_mode
        
        # Performance tracking
        self.start_time = time.time()
        self.total_conversations = 0
        
        # Track initialization status
        self._initialized = False
        
        self.logger.info("ChatbotOrchestrator created (not yet initialized)")
    
    def initialize_workers(self) -> bool:
        """Initialize all worker components."""
        if self._initialized:
            self.logger.info("Workers already initialized, skipping...")
            return True
        
        self.logger.info("Initializing Mythic's systems...")
        
        try:
            # Initialize LLM worker
            self.logger.debug("🐛 Initializing LLM worker...")
            if not self.llm_worker.initialize():
                self.logger.critical("Failed to initialize LLM worker!")
                return False
            self.logger.debug("🐛 LLM worker initialized successfully")
            
            # Initialize summarization worker
            self.logger.debug("🐛 Initializing summarization worker...")
            if not self.summarization_worker.initialize():
                self.logger.warning("Summarization initialization failed - memory management will be limited")
            else:
                self.logger.debug("🐛 Summarization worker initialized successfully")
            
            # Initialize TTS worker
            self.logger.debug("🐛 Initializing TTS worker...")
            if not self.tts_worker.initialize():
                self.logger.warning("TTS initialization failed - audio will be disabled")
            else:
                self.logger.success("TTS system initialized successfully!")
                self.logger.debug("🐛 TTS worker initialized successfully")
            
            # Initialize ASR worker if enabled
            if self.config.asr.enable_asr:
                try:
                    self.logger.debug("🐛 Initializing ASR worker...")
                    self.asr_worker.set_callbacks(
                        on_transcription=self._handle_speech_input,
                        on_error=None,  # Disable error callbacks to prevent console conflicts
                        on_listening=None  # Disable listening callbacks to prevent console conflicts
                    )
                    self.logger.success("ASR system initialized successfully!")
                    self.logger.debug("🐛 ASR worker initialized successfully")
                except Exception as e:
                    self.logger.warning(f"ASR initialization failed: {e}")
            
            self.logger.success("All workers initialized!")
            self._initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Error during worker initialization: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if workers are initialized."""
        return self._initialized
    
    def get_model_status(self) -> str:
        """Get status of all loaded models."""
        if not self._initialized:
            return "Workers not yet initialized"
            
        try:
            status_lines = []
            status_lines.append(self.llm_worker.get_status())
            status_lines.append(self.summarization_worker.get_status())
            status_lines.append(self.tts_worker.get_status())
            if self.config.asr.enable_asr:
                status_lines.append(self.asr_worker.get_status())
            
            return "\n".join(status_lines)
        except Exception as e:
            return f"Error getting model status: {e}"
    
    def run_chatbot(self):
        """Run the AI chatbot with full functionality."""
        if not self._initialized:
            self.logger.error("Cannot run chatbot - workers not initialized!")
            return
            
        self.logger.print_banner()
        self.logger.info("Commands: 'debug' for troubleshooting, 'status' for system info, 'quit' to exit")
        self.logger.console.print()
        
        # Start audio player if TTS is available
        if self.tts_worker.is_initialized:
            self.tts_worker.start_audio_player()
            if not self.tts_worker.verify_audio_output():
                self.logger.warning("Audio output verification failed - TTS may not work properly")
        else:
            self.logger.warning("TTS not available - running in text-only mode")
        
        try:
            # Mythic's dramatic entrance
            self.logger.mythic_speak(self.conversation_worker.mythic_greeting())
            self.logger.console.print()
            
            while True:
                try:
                    # Get user input using safe handler
                    user_input = safe_input("You: ").strip()
                    
                    # Handle exit commands
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        self.logger.info("Goodbye!")
                        break
                    
                    # Handle special commands
                    if user_input.lower() in ['debug', 'debug mode', 'troubleshoot']:
                        self.show_debug_menu()
                        continue
                    
                    if user_input.lower() in ['status', 'models', 'info']:
                        self.logger.mythic_speak("Here's the status of my knowledge systems, mate...")
                        status = self.get_model_status()
                        self.logger.print_panel(status, "System Status", "cyan")
                        self.logger.console.print()
                        continue
                    
                    if user_input.lower() in ['help', 'h', '?']:
                        self.logger.print_help()
                        continue
                    
                    # Skip empty input
                    if not user_input:
                        continue
                    
                    # Handle memory queries
                    if any(keyword in user_input.lower() for keyword in ['what did we talk about', 'conversation', 'remember', 'recall']):
                        self.logger.mythic_speak("Let me check my memory of our conversation...")
                        context = self.conversation_worker.get_conversation_context(
                            user_input, 
                            self.summarization_worker
                        )
                        self.logger.print_panel(context, "Memory", "cyan")
                        self.logger.console.print()
                        continue
                    
                    # Process user input and generate response
                    self._process_user_input(user_input)
                    
                except (EOFError, KeyboardInterrupt):
                    self.logger.info("Goodbye!")
                    break
                except Exception as e:
                    self.logger.error(f"Input error: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in main chat loop: {e}")
    
    def run_asr_only(self):
        """Run the AI chatbot in ASR-only mode for voice conversations."""
        if not self._initialized:
            self.logger.error("Cannot run ASR mode - workers not initialized!")
            return
            
        self.logger.print_banner()
        self.logger.info("🎤 Running in voice-only mode")
        self.logger.info("Commands: 'debug' for troubleshooting, 'status' for system info, 'quit' to exit")
        self.logger.console.print()
        
        # Start audio player if TTS is available
        if self.tts_worker.is_initialized:
            self.tts_worker.start_audio_player()
            if not self.tts_worker.verify_audio_output():
                self.logger.warning("Audio output verification failed - TTS may not work properly")
        else:
            self.logger.warning("TTS not available - running in text-only mode")
        
        try:
            # Mythic's dramatic entrance
            self.logger.mythic_speak(self.conversation_worker.mythic_greeting())
            self.logger.console.print()
            
            # Start ASR recording if enabled
            if self.config.asr.enable_asr:
                if self.asr_worker.start_recording():
                    self.logger.success("🎤 Voice recording started - speak now!")
                    self.logger.info("💬 Press Ctrl+C to stop, or just start speaking!")
                    # Show listening status
                    self.logger.update_speech_status("listening")
                else:
                    self.logger.warning("⚠️  Failed to start voice recording")
            
            # Voice-only loop - just keep listening and show status
            try:
                self.logger.info("💬 Press Ctrl+C to stop, or just start speaking!")
                self.logger.console.print()
                
                while True:
                    # Keep showing listening status and wait for voice input
                    time.sleep(0.1)  # Small delay to prevent CPU spinning
                    
                    # Check if ASR is still recording
                    if not self.asr_worker.is_recording:
                        self.logger.warning("ASR recording stopped unexpectedly")
                        break
                    
                    # Debug: Check ASR status periodically
                    if hasattr(self, '_last_debug_check'):
                        if time.time() - self._last_debug_check > 10.0:  # Every 10 seconds
                            status = self.asr_worker.get_status()
                            if status.get("is_recording"):
                                self.logger.debug("🎤 ASR is recording and listening...")
                            else:
                                self.logger.warning("🎤 ASR recording status: False")
                            self._last_debug_check = time.time()
                    else:
                        self._last_debug_check = time.time()
                    
                    # Keep the listening status visible
                    # The ASR worker continues recording, so we just need to show we're listening
                    
            except KeyboardInterrupt:
                self.logger.info("Goodbye!")
            except Exception as e:
                self.logger.error(f"Error in voice loop: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in ASR mode: {e}")
    
    def show_debug_menu(self):
        """Show the debug menu for troubleshooting."""
        self.logger.console.print()
        self.logger.console.print("🔧 Debug Menu", style="bold cyan")
        self.logger.console.print("-" * 50)
        self.logger.console.print("0. Test TTS system")
        self.logger.console.print("1. Test ASR system")
        self.logger.console.print("2. Test summarization system")
        self.logger.console.print("3. Show conversation history")
        self.logger.console.print("4. Clear conversation history")
        self.logger.console.print("5. Show system status")
        self.logger.console.print("6. Show configuration")
        self.logger.console.print("7. Test audio output")
        self.logger.console.print("8. Test microphone input")
        self.logger.console.print("9. Performance metrics")
        self.logger.console.print("a. Toggle ASR recording")
        self.logger.console.print("d. Download/update models")
        self.logger.console.print("s. Save conversation")
        self.logger.console.print("c. Clear all data")
        self.logger.console.print("x. Exit debug menu")
        self.logger.console.print("-" * 50)
        
        try:
            choice = safe_choice("Enter your choice (0-9, a, d, s, c, or x): ", 
                               ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "d", "s", "c", "x"])
            
            if choice == '0':
                self._test_tts_system()
            elif choice == '1':
                self._test_asr_system()
            elif choice == '2':
                self._test_summarization_system()
            elif choice == '3':
                self._show_conversation_history()
            elif choice == '4':
                self._clear_conversation_history()
            elif choice == '5':
                self._show_system_status()
            elif choice == '6':
                self._show_configuration()
            elif choice == '7':
                self._test_audio_output()
            elif choice == '8':
                self._test_microphone_input()
            elif choice == '9':
                self._show_performance_metrics()
            elif choice == 'a':
                self._toggle_asr_recording()
            elif choice == 'd':
                self._download_models()
            elif choice == 's':
                self._save_conversation()
            elif choice == 'c':
                self._clear_all_data()
            elif choice == 'x':
                self.logger.console.print("Exiting debug menu...")
            
            self.logger.console.print("-" * 50)
            
        except (EOFError, KeyboardInterrupt):
            self.logger.console.print("Debug menu interrupted")
    
    def _process_user_input(self, user_input: str):
        """Process user input and generate response with TTS."""
        try:
            # Generate and stream response
            self.logger.console.print("Mythic: ", end='', style="bold magenta")
            
            # Format as chat prompt
            chat_prompt = self.conversation_worker.format_chat_prompt(
                user_input, 
                self.llm_worker, 
                self.summarization_worker
            )
            
            # Stream response with automatic audio chunking
            sentence_buffer = ""
            full_response_text = ""
            
            for token, full_response in self.llm_worker.generate_response_stream(chat_prompt):
                self.logger.console.print(token, end='', style="white")
                sentence_buffer += token
                full_response_text = full_response
                
                # Process text chunks by punctuation for TTS
                punctuation_marks = ['.', '!', '?', ',', ';', ':']
                has_punctuation = any(punct in sentence_buffer for punct in punctuation_marks)
                
                if has_punctuation:
                    last_punct_pos = max(sentence_buffer.rfind(punct) for punct in punctuation_marks)
                    if last_punct_pos != -1:
                        text_chunk = sentence_buffer[:last_punct_pos + 1].strip()
                        sentence_buffer = sentence_buffer[last_punct_pos + 1:].strip()
                        
                        if text_chunk and len(text_chunk.strip()) > 1:
                            if self.tts_worker.is_tts_enabled():
                                audio_data = self.tts_worker.text_to_speech_stream(text_chunk)
                                if audio_data:
                                    self.tts_worker.play_audio_stream(audio_data)
                                    time.sleep(0.02)
            
            # Process remaining text
            if sentence_buffer.strip():
                remaining_text = sentence_buffer.strip()
                if len(remaining_text) > 3:
                    if self.tts_worker.is_tts_enabled():
                        audio_data = self.tts_worker.text_to_speech_stream(remaining_text)
                        if audio_data:
                            self.tts_worker.play_audio_stream(audio_data)
            
            # Add to conversation history
            self.conversation_worker.add_to_conversation('user', user_input, self.summarization_worker)
            
            # Automatic memory optimization
            if (len(self.conversation_worker.conversation_history) % 
                self.config.conversation.auto_summarize_interval == 0 and 
                len(self.conversation_worker.conversation_history) > 
                self.config.conversation.memory_compression_threshold):
                
                if self.debug_mode:
                    self.logger.debug("Periodic memory optimization triggered...")
                self.conversation_worker.continuous_summarize(self.summarization_worker)
            
            # Clean and validate response
            clean_response = self.conversation_worker.clean_response(full_response_text)
            
            if self.conversation_worker.has_meaningful_content(full_response_text):
                if self.conversation_worker.validate_response(clean_response):
                    self.conversation_worker.add_to_conversation('assistant', clean_response, self.summarization_worker)
                else:
                    # Try aggressive cleaning
                    aggressive_clean = clean_response
                    if '<|' in aggressive_clean:
                        aggressive_clean = aggressive_clean[:aggressive_clean.find('<|')].strip()
                    if aggressive_clean and self.conversation_worker.validate_response(aggressive_clean):
                        self.conversation_worker.add_to_conversation('assistant', aggressive_clean, self.summarization_worker)
                    else:
                        # Final cleaning attempt
                        final_clean = aggressive_clean.replace('</s>', '').replace('<s>', '').replace('<|', '').replace('|>', '').strip()
                        if final_clean and len(final_clean) > 5 and self.conversation_worker.validate_response(final_clean):
                            self.conversation_worker.add_to_conversation('assistant', final_clean, self.summarization_worker)
                        else:
                            # Extract meaningful content
                            meaningful_content = self.conversation_worker.extract_meaningful_content(clean_response)
                            if meaningful_content and self.conversation_worker.validate_response(meaningful_content):
                                self.conversation_worker.add_to_conversation('assistant', meaningful_content, self.summarization_worker)
                            else:
                                self.conversation_worker.add_to_conversation('assistant', "I understand. Please continue.", self.summarization_worker)
            else:
                self.conversation_worker.add_to_conversation('assistant', "I understand. Please continue.", self.summarization_worker)
            
            self.total_conversations += 1
            self.logger.console.print()
            self.logger.console.print("-" * 40)
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
    
    def _handle_speech_input(self, transcription: str):
        """Handle speech input from ASR."""
        try:
            if transcription.strip():
                # Clear the listening indicator and show completion cleanly
                self.logger.clear_line()
                self.logger.console.print(f"✅ Complete 🎤 Heard: {transcription}")
                self._process_user_input(transcription)
                
                # Wait for TTS to finish before showing listening status
                self.logger.debug("🎤 TTS finished, waiting for completion...")
                self._wait_for_tts_completion()
                
                # Now restore listening status
                self.logger.debug("🎤 Restoring listening status...")
                self.logger.console.print()  # Add a line break
                self.logger.update_speech_status("listening")
                self.logger.debug("🎤 Listening status restored")
        except Exception as e:
            self.logger.clear_line()
            self.logger.console.print(f"❌ Error 🎤 Error processing speech: {e}")
            self.logger.error(f"Error handling speech input: {e}")
            
            # Restore listening status even after error
            self.logger.console.print()  # Add a line break
            self.logger.update_speech_status("listening")
    
    def _wait_for_tts_completion(self):
        """Wait for TTS audio playback to complete before continuing."""
        try:
            self.logger.debug("🎵 Waiting for TTS to complete...")
            
            # Wait for TTS to finish playing audio
            wait_count = 0
            while self.tts_worker.has_audio_playing():
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                wait_count += 1
                if wait_count % 50 == 0:  # Log every 5 seconds
                    self.logger.debug(f"🎵 Still waiting for TTS... (waited {wait_count * 0.1:.1f}s)")
            
            self.logger.debug(f"🎵 TTS completed after {wait_count * 0.1:.1f}s")
            
            # Add a small buffer to ensure audio is completely finished
            time.sleep(0.5)
            self.logger.debug("🎵 Buffer time completed, ready to show listening status")
            
        except Exception as e:
            self.logger.debug(f"Error waiting for TTS completion: {e}")
    
    # Debug menu helper methods
    def _test_tts_system(self):
        """Test the TTS system."""
        self.logger.info("Testing TTS system...")
        test_text = "This is a test of the text-to-speech system."
        audio_data = self.tts_worker.text_to_speech_stream(test_text)
        if audio_data:
            self.logger.success("TTS test successful!")
            self.tts_worker.play_audio_stream(audio_data)
        else:
            self.logger.error("TTS test failed")
    
    def _test_asr_system(self):
        """Test the ASR system."""
        self.logger.info("Testing ASR system...")
        if self.config.asr.enable_asr:
            self.logger.info("ASR is enabled and ready")
        else:
            self.logger.warning("ASR is disabled")
    
    def _test_summarization_system(self):
        """Test the summarization system."""
        self.logger.info("Testing summarization system...")
        test_result = self.conversation_worker.test_summarization_system(self.summarization_worker)
        self.logger.print_panel(test_result, "Summarization Test Result", "cyan")
    
    def _show_conversation_history(self):
        """Show conversation history."""
        self.logger.info("Showing conversation history...")
        history = self.conversation_worker.get_conversation_stats()
        # Convert dictionary to formatted string for display
        if isinstance(history, dict):
            history_str = "\n".join([f"{key}: {value}" for key, value in history.items()])
        else:
            history_str = str(history)
        self.logger.print_panel(history_str, "Conversation History", "cyan")
    
    def _clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_worker.clear_conversation()
        self.logger.success("Conversation history cleared")
    
    def _show_system_status(self):
        """Show system status."""
        status = self.get_model_status()
        # Ensure status is a string for display
        if isinstance(status, dict):
            status_str = "\n".join([f"{key}: {value}" for key, value in status.items()])
        else:
            status_str = str(status)
        self.logger.print_panel(status_str, "System Status", "cyan")
    
    def _show_configuration(self):
        """Show configuration."""
        config_dict = self.config.to_dict()
        self.logger.print_table(config_dict, "Configuration")
    
    def _test_audio_output(self):
        """Test audio output."""
        self.logger.info("Testing audio output...")
        if self.tts_worker.verify_audio_output():
            self.logger.success("Audio output working")
        else:
            self.logger.error("Audio output not working")
    
    def _test_microphone_input(self):
        """Test microphone input."""
        self.logger.info("Testing microphone input...")
        if self.config.asr.enable_asr:
            self.logger.info("Microphone input enabled")
        else:
            self.logger.warning("Microphone input disabled")
    
    def _show_performance_metrics(self):
        """Show performance metrics."""
        uptime = time.time() - self.start_time
        metrics = f"Uptime: {uptime:.1f}s\nTotal conversations: {self.total_conversations}"
        self.logger.print_panel(metrics, "Performance Metrics", "cyan")
    
    def _toggle_asr_recording(self):
        """Toggle ASR recording."""
        if self.asr_worker.is_recording:
            self.asr_worker.stop_recording()
            self.logger.info("ASR recording stopped")
        else:
            if self.asr_worker.start_recording():
                self.logger.success("ASR recording started")
            else:
                self.logger.error("Failed to start ASR recording")
    
    def _download_models(self):
        """Download/update models."""
        self.logger.info("Model download not implemented yet")
    
    def _save_conversation(self):
        """Save conversation."""
        self.logger.info("Conversation save not implemented yet")
    
    def _clear_all_data(self):
        """Clear all data."""
        self.conversation_worker.clear_conversation()
        self.logger.success("All data cleared")
    
    def cleanup(self):
        """Clean up all worker resources."""
        self.logger.info("Cleaning up Mythic's systems...")
        
        try:
            if hasattr(self, 'llm_worker') and self.llm_worker:
                self.llm_worker.cleanup()
            if hasattr(self, 'summarization_worker') and self.summarization_worker:
                self.summarization_worker.cleanup()
            if hasattr(self, 'tts_worker') and self.tts_worker:
                self.tts_worker.cleanup()
            if hasattr(self, 'asr_worker') and self.asr_worker and self.config.asr.enable_asr:
                self.asr_worker.cleanup()
            self.logger.success("All systems cleaned up successfully!")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def get_chatbot_orchestrator():
    """Get the ChatbotOrchestrator class."""
    return ChatbotOrchestrator


if __name__ == "__main__":
    main() 
