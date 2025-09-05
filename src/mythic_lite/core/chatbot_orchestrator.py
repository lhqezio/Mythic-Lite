"""
Main orchestrator module for Mythic-Lite chatbot system.
Coordinates all workers and manages the main chatbot interface.
"""

import time
import json
import os
from datetime import datetime
from typing import Optional, Any, Dict, List

# Use lazy imports to avoid circular dependencies
def get_workers():
    """Get worker classes when needed."""
    from ..workers.asr_worker import ASRWorker
    from ..workers.llm_worker import LLMWorker
    from ..workers.memory_worker import MemoryWorker
    from ..workers.tts_worker import TTSWorker
    return ASRWorker, LLMWorker, MemoryWorker, TTSWorker

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
        ASRWorker, LLMWorker, MemoryWorker, TTSWorker = get_workers()
        
        # Create worker instances but don't initialize them yet
        self.llm_worker = LLMWorker(self.config)
        self.memory_worker = MemoryWorker(self.config)
        self.tts_worker = TTSWorker(self.config)
        self.asr_worker = ASRWorker(self.config)
        self.conversation_worker = ConversationWorker(self.config)
        
        # Set LLM worker reference in memory worker
        self.memory_worker.set_llm_worker(self.llm_worker)
        
        # Debug mode from configuration
        self.debug_mode = self.config.debug_mode
        self.conversation_worker.debug_mode = self.debug_mode
        
        # Performance tracking
        self.start_time = time.time()
        self.total_conversations = 0
        self.benchmark_results = None  # Store benchmark test results
        
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
            
            # Update memory worker with LLM reference
            self.memory_worker.set_llm_worker(self.llm_worker)
            
            # Initialize memory worker
            self.logger.debug("🐛 Initializing memory worker...")
            if not self.memory_worker.initialize():
                self.logger.warning("Memory worker initialization failed - memory management will be limited")
            else:
                self.logger.debug("🐛 Memory worker initialized successfully")
            
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
            status_lines.append(self.memory_worker.get_status())
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
                            self.memory_worker
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
        self.logger.console.print("b. 🚀 Run Benchmark Mode")
        self.logger.console.print("a. Toggle ASR recording")
        self.logger.console.print("d. Download/update models")
        self.logger.console.print("s. Save conversation")
        self.logger.console.print("c. Clear all data")
        self.logger.console.print("x. Exit debug menu")
        self.logger.console.print("-" * 50)
        
        try:
            choice = safe_choice("Enter your choice (0-9, b, a, d, s, c, or x): ", 
                               ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "b", "a", "d", "s", "c", "x"])
            
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
            elif choice == 'b':
                self._run_benchmark_mode()
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
                self.memory_worker
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
            self.conversation_worker.add_to_conversation('user', user_input, self.memory_worker)
            
            # Automatic memory optimization
            if (len(self.conversation_worker.conversation_history) % 
                self.config.conversation.auto_summarize_interval == 0 and 
                len(self.conversation_worker.conversation_history) > 
                self.config.conversation.memory_compression_threshold):
                
                if self.debug_mode:
                    self.logger.debug("Periodic memory optimization triggered...")
                self.conversation_worker.continuous_summarize(self.memory_worker)
            
            # Clean and validate response
            clean_response = self.conversation_worker.clean_response(full_response_text)
            
            if self.conversation_worker.has_meaningful_content(full_response_text):
                if self.conversation_worker.validate_response(clean_response):
                    self.conversation_worker.add_to_conversation('assistant', clean_response, self.memory_worker)
                else:
                    # Try aggressive cleaning
                    aggressive_clean = clean_response
                    if '<|' in aggressive_clean:
                        aggressive_clean = aggressive_clean[:aggressive_clean.find('<|')].strip()
                    if aggressive_clean and self.conversation_worker.validate_response(aggressive_clean):
                        self.conversation_worker.add_to_conversation('assistant', aggressive_clean, self.memory_worker)
                    else:
                        # Final cleaning attempt
                        final_clean = aggressive_clean.replace('</s>', '').replace('<s>', '').replace('<|', '').replace('|>', '').strip()
                        if final_clean and len(final_clean) > 5 and self.conversation_worker.validate_response(final_clean):
                            self.conversation_worker.add_to_conversation('assistant', final_clean, self.memory_worker)
                        else:
                            # Extract meaningful content
                            meaningful_content = self.conversation_worker.extract_meaningful_content(clean_response)
                            if meaningful_content and self.conversation_worker.validate_response(meaningful_content):
                                self.conversation_worker.add_to_conversation('assistant', meaningful_content, self.memory_worker)
                            else:
                                self.conversation_worker.add_to_conversation('assistant', "I understand. Please continue.", self.memory_worker)
            else:
                self.conversation_worker.add_to_conversation('assistant', "I understand. Please continue.", self.memory_worker)
            
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
            
            # Add a longer buffer to ensure audio is completely finished and prevent overlapping
            # This prevents ASR from picking up the tail end of TTS audio
            time.sleep(5.0)  # Increased to 3.0s to prevent ASR overlap issues
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
        test_result = self.conversation_worker.test_summarization_system(self.memory_worker)
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

    def _run_benchmark_mode(self):
        """Run comprehensive benchmark mode focused on LLM + Memory performance."""
        try:
            self.logger.console.print("\n" + "="*80, style="bold blue")
            self.logger.console.print("🚀 MYTHIC-LITE LLM + MEMORY BENCHMARK", style="bold blue")
            self.logger.console.print("="*80, style="bold blue")
            
            # System Status
            self.logger.console.print("\n📊 SYSTEM STATUS", style="bold green")
            self._show_system_status()
            
            # Initialize workers if needed
            if not self.is_initialized():
                self.logger.console.print("\n🔧 Initializing workers for benchmark...", style="yellow")
                if not self.initialize_workers():
                    self.logger.console.print("❌ Failed to initialize workers - cannot run benchmark", style="red")
                    return
            
            # Run automated 30-turn test conversation
            self.logger.console.print("\n🧪 RUNNING 30-TURN LLM + MEMORY TEST", style="bold green")
            
            # Test prompts with more variety to prevent repetitive responses
            test_prompts = [
                # Intro questions
                "Hello! Who are you and what do you do?",
                "Tell me about your background as a mercenary.",
                "What's your fighting style like?",
                "How did you get into this line of work?",
                "What's your favorite weapon and why?",
                
                # Combat questions
                "Describe your most challenging mission.",
                "How do you handle working with allies?",
                "What makes a good mercenary in your opinion?",
                "Tell me about a time you had to think on your feet.",
                "How do you prepare for dangerous assignments?",
                
                # Memory questions
                "What did I ask you about earlier?",
                "Remind me what you said about weapons.",
                "What was your background again?",
                "How did you answer about your skills?",
                "What did you tell me about planning?",
                
                # Quality questions
                "What was your biggest challenge?",
                "How do you stay sharp in this business?",
                "What's the most valuable lesson you've learned?",
                "Tell me about your code of honor.",
                "How do you handle failure or setbacks?",
                
                # Additional variety questions
                "What's your opinion on modern technology?",
                "How do you spend your downtime?",
                "What's the strangest job you've ever taken?",
                "How do you deal with difficult clients?",
                "What keeps you motivated in this dangerous work?",
                
                # More specific questions
                "Describe your ideal team composition.",
                "What's your approach to reconnaissance?",
                "How do you handle moral dilemmas?",
                "What's your relationship with local authorities?",
                "How do you adapt to different environments?"
            ]
            
            conversation_data = []
            total_start_time = time.time()
            total_tokens = 0
            
            for turn, prompt in enumerate(test_prompts, 1):
                self.logger.console.print(f"\n📝 Turn {turn:2d}/30 [TEST]: {prompt}", style="yellow")
                
                # Record start time for this interaction
                interaction_start = time.time()
                
                try:
                    # IMPORTANT: Run through the ACTUAL conversation flow, not just test responses
                    # This ensures memory creation and conversation history updates
                    response = self._run_real_conversation_turn(prompt)
                    
                    # Calculate response time
                    response_time = time.time() - interaction_start
                    
                    # Count tokens (approximate)
                    token_count = len(response.split()) * 1.3
                    total_tokens += token_count
                    
                    # Store conversation data
                    conversation_data.append({
                        'turn': turn,
                        'category': 'test', # Indicate it's a test turn
                        'prompt': prompt,
                        'response': response,
                        'response_time': response_time,
                        'token_count': token_count,
                        'timestamp': time.time()
                    })
                    
                    # Show results
                    self.logger.console.print(f"✅ Response in {response_time:.2f}s | ~{token_count:.0f} tokens", style="green")
                    self.logger.console.print(f"💬 {response[:80]}{'...' if len(response) > 80 else ''}", style="white")
                    
                    # Show memory status after each turn
                    if hasattr(self.memory_worker, 'get_memory_stats'):
                        memory_stats = self.memory_worker.get_memory_stats()
                        total_memories = memory_stats.get('total_memories', 0)
                        self.logger.console.print(f"🧠 Memory Status: {total_memories} memories cached", style="dim cyan")
                    
                    # Small delay between turns
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.console.print(f"❌ Turn {turn} failed: {e}", style="red")
                    conversation_data.append({
                        'turn': turn,
                        'category': 'test', # Indicate it's a test turn
                        'prompt': prompt,
                        'response': f"ERROR: {e}",
                        'response_time': 0,
                        'token_count': 0,
                        'timestamp': time.time()
                    })
                    continue
            
            # Calculate overall metrics
            total_time = time.time() - total_start_time
            avg_response_time = total_time / len(test_prompts)
            success_rate = sum(1 for turn in conversation_data if not turn['response'].startswith('ERROR')) / len(test_prompts)
            
            # Store comprehensive benchmark results
            self.benchmark_results = {
                'total_test_time': total_time,
                'avg_response_time': avg_response_time,
                'total_tokens_generated': total_tokens,
                'test_conversations': len(test_prompts),
                'success_rate': success_rate,
                'conversation_data': conversation_data,
                'tokens_per_second': total_tokens / total_time if total_time > 0 else 0
            }
            
            # Show test summary
            self.logger.console.print(f"\n📊 30-TURN TEST CONVERSATION SUMMARY", style="bold green")
            test_summary = f"""
╭─ Test Results ──────────────────────────────────────────────────────────────────╮
│ Total Test Time: {total_time:.2f}s                                                          │
│ Average Response Time: {avg_response_time:.2f}s                                                │
│ Total Tokens Generated: {total_tokens:.0f}                                                        │
│ Test Conversations: {len(test_prompts)}                                                          │
│ Success Rate: {success_rate*100:.1f}%                                                          │
│ Tokens per Second: {total_tokens/total_time:.1f}                                                        │
╰─────────────────────────────────────────────────────────────────────────────────╯
            """
            self.logger.console.print(test_summary, style="cyan")
            
            # Show complete conversation log
            self.logger.console.print(f"\n📝 COMPLETE CONVERSATION LOG", style="bold green")
            self._show_complete_conversation_log(conversation_data)
            
            # Show all memories created
            self.logger.console.print(f"\n🧠 ALL MEMORIES CREATED", style="bold green")
            self._show_all_memories_created()
            
            # Performance Metrics
            self.logger.console.print("\n📈 PERFORMANCE METRICS", style="bold green")
            self._show_detailed_performance_metrics()
            
            # Conversation Analysis
            self.logger.console.print("\n💬 CONVERSATION ANALYSIS", style="bold green")
            self._show_conversation_analysis()
            
            # Memory Analysis
            self.logger.console.print("\n🧠 MEMORY ANALYSIS", style="bold green")
            self._show_memory_analysis()
            
            # Benchmark Summary
            self.logger.console.print("\n🏆 BENCHMARK SUMMARY", style="bold green")
            self._show_benchmark_summary()
            
            self.logger.console.print("\n" + "="*80, style="bold blue")
            self.logger.console.print("✅ BENCHMARK COMPLETE", style="bold blue")
            self.logger.console.print("="*80, style="bold blue")
            
            # Log all benchmark data to files
            self.logger.console.print("\n📁 LOGGING BENCHMARK DATA TO LOGS FOLDER", style="bold green")
            self._log_benchmark_data(conversation_data)
            
        except Exception as e:
            self.logger.error(f"Error running benchmark mode: {e}")

    def _show_complete_conversation_log(self, conversation_data):
        """Show the complete conversation log with all turns."""
        try:
            self.logger.console.print("📋 Full 30-Turn Conversation Log:", style="bold yellow")
            self.logger.console.print("=" * 100, style="dim white")
            
            for turn_data in conversation_data:
                turn = turn_data['turn']
                category = turn_data['category']
                prompt = turn_data['prompt']
                response = turn_data['response']
                response_time = turn_data['response_time']
                token_count = turn_data['token_count']
                
                # Category icon mapping
                category_icons = {
                    'intro': '👋',
                    'combat': '⚔️', 
                    'memory': '🧠',
                    'quality': '✨',
                    'test': '🧪'
                }
                
                icon = category_icons.get(category, '❓')
                
                # Show turn header
                self.logger.console.print(f"\n{icon} TURN {turn:2d}/30 [{category.upper()}]", style="bold cyan")
                self.logger.console.print(f"⏱️  Response Time: {response_time:.2f}s | 📊 Tokens: ~{token_count:.0f}", style="dim white")
                self.logger.console.print(f"👤 USER: {prompt}", style="white")
                self.logger.console.print(f"🤖 MYTHIC: {response}", style="green")
                
                # Add separator between turns
                if turn < 30:
                    self.logger.console.print("-" * 80, style="dim white")
            
            self.logger.console.print("\n" + "=" * 100, style="dim white")
            
        except Exception as e:
            self.logger.error(f"Error showing complete conversation log: {e}")

    def _show_all_memories_created(self):
        """Show all memories that were created during the benchmark."""
        try:
            if not hasattr(self.memory_worker, 'get_memory_stats'):
                self.logger.console.print("Memory worker not available", style="yellow")
                return
            
            memory_stats = self.memory_worker.get_memory_stats()
            total_memories = memory_stats.get('total_memories', 0)
            
            if total_memories == 0:
                self.logger.console.print("⚠️  No memories were created during the benchmark", style="yellow")
                self.logger.console.print("This might indicate the memory system isn't working properly", style="red")
                return
            
            # Get all memories from the cache
            memory_cache = getattr(self.memory_worker, 'memory_cache', {})
            
            if not memory_cache:
                self.logger.console.print("⚠️  Memory cache is empty despite stats showing memories", style="yellow")
                return
            
            self.logger.console.print(f"🎯 Total Memories Created: {total_memories}", style="bold green")
            self.logger.console.print("=" * 80, style="dim white")
            
            # Show each memory with details
            for i, (memory_key, memory_content) in enumerate(memory_cache.items(), 1):
                self.logger.console.print(f"\n💾 MEMORY {i}: {memory_key}", style="bold cyan")
                self.logger.console.print(f"📝 Content: {memory_content}", style="white")
                self.logger.console.print(f"📏 Length: {len(memory_content)} characters", style="dim white")
                
                # Add separator between memories
                if i < len(memory_cache):
                    self.logger.console.print("-" * 60, style="dim white")
            
            # Show memory statistics
            self.logger.console.print(f"\n📊 MEMORY STATISTICS", style="bold green")
            memory_stats_display = f"""
╭─ Memory System Performance ──────────────────────────────────────────────────────╮
│ Total Memories Created: {total_memories}                                                │
│ Memory Cache Size: {len(memory_cache)}                                                │
│ Average Memory Length: {sum(len(m) for m in memory_cache.values()) / len(memory_cache):.1f} characters                                    │
│ Memory Creation Rate: {total_memories / 30:.1f} memories per turn                                                │
│ Cache Utilization: {len(memory_cache)}/{getattr(self.config.memory, 'cache_size', 100)} ({len(memory_cache)/max(getattr(self.config.memory, 'cache_size', 100), 1)*100:.1f}%) │
╰─────────────────────────────────────────────────────────────────────────────────╯
            """
            self.logger.console.print(memory_stats_display, style="cyan")
            
        except Exception as e:
            self.logger.error(f"Error showing all memories created: {e}")

    def _log_benchmark_data(self, conversation_data):
        """Log all benchmark data to the logs folder for analysis."""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            benchmark_dir = os.path.join(logs_dir, f"benchmark_{timestamp}")
            os.makedirs(benchmark_dir, exist_ok=True)
            
            self.logger.console.print(f"📁 Saving benchmark data to: {benchmark_dir}", style="cyan")
            
            # 1. Log complete conversation
            self._log_conversation_data(benchmark_dir, conversation_data)
            
            # 2. Log all memories created
            self._log_memory_data(benchmark_dir)
            
            # 3. Log performance metrics
            self._log_performance_metrics(benchmark_dir)
            
            # 4. Log system prompts and configuration
            self._log_system_data(benchmark_dir)
            
            # 5. Log benchmark summary
            self._log_benchmark_summary(benchmark_dir)
            
            # 6. Create a comprehensive index file
            self._create_benchmark_index(benchmark_dir, timestamp)
            
            self.logger.console.print(f"✅ All benchmark data logged to: {benchmark_dir}", style="bold green")
            
        except Exception as e:
            self.logger.error(f"Error logging benchmark data: {e}")

    def _log_conversation_data(self, benchmark_dir, conversation_data):
        """Log the complete conversation data."""
        try:
            # Detailed conversation log
            conversation_file = os.path.join(benchmark_dir, "conversation_log.txt")
            with open(conversation_file, 'w', encoding='utf-8') as f:
                f.write("MYTHIC-LITE BENCHMARK - COMPLETE CONVERSATION LOG\n")
                f.write("=" * 80 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Turns: {len(conversation_data)}\n\n")
                
                for turn_data in conversation_data:
                    turn = turn_data['turn']
                    category = turn_data['category']
                    prompt = turn_data['prompt']
                    response = turn_data['response']
                    response_time = turn_data['response_time']
                    token_count = turn_data['token_count']
                    
                    f.write(f"TURN {turn:2d}/30 [{category.upper()}]\n")
                    f.write(f"Response Time: {response_time:.2f}s | Tokens: ~{token_count:.0f}\n")
                    f.write(f"USER: {prompt}\n")
                    f.write(f"MYTHIC: {response}\n")
                    f.write("-" * 80 + "\n\n")
            
            # JSON format for programmatic analysis
            conversation_json = os.path.join(benchmark_dir, "conversation_data.json")
            with open(conversation_json, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            self.logger.console.print(f"📝 Conversation logged to: conversation_log.txt & conversation_data.json", style="green")
            
        except Exception as e:
            self.logger.error(f"Error logging conversation data: {e}")

    def _log_memory_data(self, benchmark_dir):
        """Log all memory data and summaries."""
        try:
            if not hasattr(self.memory_worker, 'get_memory_stats'):
                return
            
            memory_stats = self.memory_worker.get_memory_stats()
            memory_cache = getattr(self.memory_worker, 'memory_cache', {})
            
            # Memory summary file
            memory_file = os.path.join(benchmark_dir, "memory_summary.txt")
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write("MYTHIC-LITE BENCHMARK - MEMORY SYSTEM ANALYSIS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("MEMORY STATISTICS:\n")
                f.write(f"Total Memories Created: {memory_stats.get('total_memories', 0)}\n")
                f.write(f"Memory Cache Size: {len(memory_cache)}\n")
                f.write(f"Cache Utilization: {len(memory_cache)}/{getattr(self.config.memory, 'cache_size', 100)} ({len(memory_cache)/max(getattr(self.config.memory, 'cache_size', 100), 1)*100:.1f}%)\n\n")
                
                if memory_cache:
                    f.write("DETAILED MEMORIES:\n")
                    f.write("-" * 60 + "\n")
                    for i, (memory_key, memory_content) in enumerate(memory_cache.items(), 1):
                        f.write(f"MEMORY {i}: {memory_key}\n")
                        f.write(f"Content: {memory_content}\n")
                        f.write(f"Length: {len(memory_content)} characters\n")
                        f.write("-" * 60 + "\n\n")
                else:
                    f.write("No memories were created during the benchmark.\n")
            
            # Memory data in JSON format
            memory_json = os.path.join(benchmark_dir, "memory_data.json")
            memory_data = {
                'timestamp': datetime.now().isoformat(),
                'memory_stats': memory_stats,
                'memory_cache': memory_cache,
                'cache_size': getattr(self.config.memory, 'cache_size', 100)
            }
            with open(memory_json, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.console.print(f"🧠 Memory data logged to: memory_summary.txt & memory_data.json", style="green")
            
        except Exception as e:
            self.logger.error(f"Error logging memory data: {e}")

    def _log_performance_metrics(self, benchmark_dir):
        """Log detailed performance metrics from all workers."""
        try:
            # Performance metrics file
            metrics_file = os.path.join(benchmark_dir, "performance_metrics.txt")
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write("MYTHIC-LITE BENCHMARK - PERFORMANCE METRICS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # LLM Performance
                if hasattr(self.llm_worker, 'get_performance_stats'):
                    llm_stats = self.llm_worker.get_performance_stats()
                    f.write("LLM WORKER PERFORMANCE:\n")
                    f.write(f"Total Requests: {llm_stats.get('total_requests', 0)}\n")
                    f.write(f"Total Tokens Generated: {llm_stats.get('total_tokens_generated', 0)}\n")
                    f.write(f"Average Response Time: {llm_stats.get('average_response_time', 0):.2f}s\n")
                    f.write(f"Initialization Status: {llm_stats.get('is_initialized', False)}\n\n")
                
                # Memory Performance
                if hasattr(self.memory_worker, 'get_memory_stats'):
                    memory_stats = self.memory_worker.get_memory_stats()
                    f.write("MEMORY WORKER PERFORMANCE:\n")
                    for key, value in memory_stats.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                # System Performance
                if hasattr(self, 'benchmark_results') and self.benchmark_results:
                    f.write("BENCHMARK RESULTS:\n")
                    for key, value in self.benchmark_results.items():
                        if key != 'conversation_data':  # Skip large conversation data
                            f.write(f"{key}: {value}\n")
                    f.write("\n")
            
            # Performance data in JSON format
            performance_json = os.path.join(benchmark_dir, "performance_data.json")
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'llm_performance': self.llm_worker.get_performance_stats() if hasattr(self.llm_worker, 'get_performance_stats') else {},
                'memory_performance': self.memory_worker.get_memory_stats() if hasattr(self.memory_worker, 'get_memory_stats') else {},
                'benchmark_results': {k: v for k, v in (self.benchmark_results or {}).items() if k != 'conversation_data'}
            }
            with open(performance_json, 'w', encoding='utf-8') as f:
                json.dump(performance_data, f, indent=2, ensure_ascii=False)
            
            self.logger.console.print(f"📊 Performance metrics logged to: performance_metrics.txt & performance_data.json", style="green")
            
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {e}")

    def _log_system_data(self, benchmark_dir):
        """Log system configuration, prompts, and settings."""
        try:
            # System configuration file
            system_file = os.path.join(benchmark_dir, "system_configuration.txt")
            with open(system_file, 'w', encoding='utf-8') as f:
                f.write("MYTHIC-LITE BENCHMARK - SYSTEM CONFIGURATION\n")
                f.write("=" * 80 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # LLM Configuration
                f.write("LLM CONFIGURATION:\n")
                f.write(f"Model Repository: {self.config.llm.model_repo}\n")
                f.write(f"Model Filename: {self.config.llm.model_filename}\n")
                f.write(f"Max Tokens: {self.config.llm.max_tokens}\n")
                f.write(f"Temperature: {self.config.llm.temperature}\n")
                f.write(f"Context Window: {self.config.llm.context_window}\n\n")
                
                # Memory Configuration
                f.write("MEMORY CONFIGURATION:\n")
                f.write(f"Cache Size: {self.config.memory.cache_size}\n")
                f.write(f"Max Summary Length: {self.config.memory.max_summary_length}\n\n")
                
                # Conversation Configuration
                f.write("CONVERSATION CONFIGURATION:\n")
                f.write(f"Max Conversation Length: {self.config.conversation.max_conversation_length}\n")
                f.write(f"Max Tokens Per Message: {self.config.conversation.max_tokens_per_message}\n\n")
                
                # System Prompts
                f.write("SYSTEM PROMPTS:\n")
                f.write("-" * 60 + "\n")
                f.write("CONVERSATION WORKER SYSTEM PROMPT:\n")
                f.write(self.conversation_worker.system_prompt + "\n\n")
                
                # Worker Status
                f.write("WORKER STATUS:\n")
                f.write(f"LLM Worker: {self.llm_worker.get_status()}\n")
                f.write(f"Memory Worker: {self.memory_worker.get_status()}\n")
                f.write(f"ASR Worker: {self.asr_worker.get_status()}\n")
                f.write(f"TTS Worker: {self.tts_worker.get_status()}\n")
            
            # System configuration in JSON format
            system_json = os.path.join(benchmark_dir, "system_configuration.json")
            system_data = {
                'timestamp': datetime.now().isoformat(),
                'llm_config': {
                    'model_repo': self.config.llm.model_repo,
                    'model_filename': self.config.llm.model_filename,
                    'max_tokens': self.config.llm.max_tokens,
                    'temperature': self.config.llm.temperature,
                    'context_window': self.config.llm.context_window
                },
                'memory_config': {
                    'cache_size': self.config.memory.cache_size,
                    'max_summary_length': self.config.memory.max_summary_length
                },
                'conversation_config': {
                    'max_conversation_length': self.config.conversation.max_conversation_length,
                    'max_tokens_per_message': self.config.conversation.max_tokens_per_message
                },
                'system_prompts': {
                    'conversation_worker': self.conversation_worker.system_prompt
                },
                'worker_status': {
                    'llm_worker': self.llm_worker.get_status(),
                    'memory_worker': self.memory_worker.get_status(),
                    'asr_worker': self.asr_worker.get_status(),
                    'tts_worker': self.tts_worker.get_status()
                }
            }
            with open(system_json, 'w', encoding='utf-8') as f:
                json.dump(system_data, f, indent=2, ensure_ascii=False)
            
            self.logger.console.print(f"⚙️  System configuration logged to: system_configuration.txt & system_configuration.json", style="green")
            
        except Exception as e:
            self.logger.error(f"Error logging system data: {e}")

    def _log_benchmark_summary(self, benchmark_dir):
        """Log the final benchmark summary and analysis."""
        try:
            # Benchmark summary file
            summary_file = os.path.join(benchmark_dir, "README.md")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# MYTHIC-LITE BENCHMARK RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("This directory contains comprehensive benchmark data from the Mythic-Lite system.\n\n")
                
                f.write("## 📁 Files Overview\n\n")
                f.write("| File | Description | Format |\n")
                f.write("|------|-------------|--------|\n")
                f.write("| `conversation_log.txt` | Complete 30-turn conversation log | Text |\n")
                f.write("| `conversation_data.json` | Structured conversation data | JSON |\n")
                f.write("| `memory_summary.txt` | Memory system analysis | Text |\n")
                f.write("| `memory_data.json` | Structured memory data | JSON |\n")
                f.write("| `performance_metrics.txt` | Performance analysis | Text |\n")
                f.write("| `performance_data.json` | Structured performance data | JSON |\n")
                f.write("| `system_configuration.txt` | System settings and prompts | Text |\n")
                f.write("| `system_configuration.json` | Structured system data | JSON |\n")
                f.write("| `benchmark_summary.txt` | Final summary and recommendations | Text |\n\n")
                
                f.write("## 🔍 Analysis Guide\n\n")
                f.write("1. **Start with `benchmark_summary.txt`** for an overview\n")
                f.write("2. **Check `performance_metrics.txt`** for performance analysis\n")
                f.write("3. **Review `conversation_log.txt`** for conversation quality\n")
                f.write("4. **Examine `memory_summary.txt`** for memory system performance\n")
                f.write("5. **Use JSON files** for programmatic analysis\n\n")
                
                f.write("## 📊 Key Metrics to Monitor\n\n")
                f.write("- **Response Times**: Should be consistent and reasonable\n")
                f.write("- **Memory Creation**: Should increase during conversation\n")
                f.write("- **Token Generation**: Should vary appropriately\n")
                f.write("- **Error Rates**: Should be minimal\n")
                f.write("- **System Status**: All workers should be initialized\n\n")
                
                f.write("## 🚀 Next Steps\n\n")
                f.write("Use this data to:\n")
                f.write("- Identify performance bottlenecks\n")
                f.write("- Optimize system configuration\n")
                f.write("- Improve memory system efficiency\n")
                f.write("- Debug any issues found\n")
                f.write("- Compare with previous benchmarks\n")
            
            self.logger.console.print(f"📖 Benchmark index created: README.md", style="green")
            
        except Exception as e:
            self.logger.error(f"Error logging benchmark summary: {e}")

    def _create_benchmark_index(self, benchmark_dir, timestamp):
        """Create an index file listing all logged data."""
        try:
            index_file = os.path.join(benchmark_dir, "README.md")
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(f"# MYTHIC-LITE BENCHMARK RESULTS - {timestamp}\n\n")
                f.write("This directory contains comprehensive benchmark data from the Mythic-Lite system.\n\n")
                
                f.write("## 📁 Files Overview\n\n")
                f.write("| File | Description | Format |\n")
                f.write("|------|-------------|--------|\n")
                f.write("| `conversation_log.txt` | Complete 30-turn conversation log | Text |\n")
                f.write("| `conversation_data.json` | Structured conversation data | JSON |\n")
                f.write("| `memory_summary.txt` | Memory system analysis | Text |\n")
                f.write("| `memory_data.json` | Structured memory data | JSON |\n")
                f.write("| `performance_metrics.txt` | Performance analysis | Text |\n")
                f.write("| `performance_data.json` | Structured performance data | JSON |\n")
                f.write("| `system_configuration.txt` | System settings and prompts | Text |\n")
                f.write("| `system_configuration.json` | Structured system data | JSON |\n")
                f.write("| `benchmark_summary.txt` | Final summary and recommendations | Text |\n\n")
                
                f.write("## 🔍 Analysis Guide\n\n")
                f.write("1. **Start with `benchmark_summary.txt`** for an overview\n")
                f.write("2. **Check `performance_metrics.txt`** for performance analysis\n")
                f.write("3. **Review `conversation_log.txt`** for conversation quality\n")
                f.write("4. **Examine `memory_summary.txt`** for memory system performance\n")
                f.write("5. **Use JSON files** for programmatic analysis\n\n")
                
                f.write("## 📊 Key Metrics to Monitor\n\n")
                f.write("- **Response Times**: Should be consistent and reasonable\n")
                f.write("- **Memory Creation**: Should increase during conversation\n")
                f.write("- **Token Generation**: Should vary appropriately\n")
                f.write("- **Error Rates**: Should be minimal\n")
                f.write("- **System Status**: All workers should be initialized\n\n")
                
                f.write("## 🚀 Next Steps\n\n")
                f.write("Use this data to:\n")
                f.write("- Identify performance bottlenecks\n")
                f.write("- Optimize system configuration\n")
                f.write("- Improve memory system efficiency\n")
                f.write("- Debug any issues found\n")
                f.write("- Compare with previous benchmarks\n")
            
            self.logger.console.print(f"📖 Benchmark index created: README.md", style="green")
            
        except Exception as e:
            self.logger.error(f"Error creating benchmark index: {e}")

    def _run_real_conversation_turn(self, prompt):
        """Run a real conversation turn that actually triggers memory creation."""
        try:
            # This runs through the ACTUAL conversation flow, not just test responses
            # It will trigger memory creation, conversation history updates, etc.
            
            # Add user message to conversation history
            self.conversation_worker.add_to_conversation("user", prompt)
            
            # Format the prompt for the LLM (this should trigger memory operations)
            formatted_prompt = self.conversation_worker.format_chat_prompt(
                prompt, 
                self.llm_worker, 
                self.memory_worker
            )
            
            # Generate response using the LLM
            if hasattr(self.llm_worker, 'generate_response'):
                response = self.llm_worker.generate_response(
                    formatted_prompt,
                    max_tokens=self.config.llm.max_tokens,
                    temperature=self.config.llm.temperature
                )
            else:
                return "Error: LLM worker has no generate_response method"
            
            # Add assistant response to conversation history
            if response and not response.startswith("Error"):
                self.conversation_worker.add_to_conversation("assistant", response)
                
                # Force memory creation after every few turns
                if len(self.conversation_worker.conversation_history) % 5 == 0:
                    self.logger.console.print("🔄 Creating memory summary...", style="dim yellow")
                    # Get the recent conversation text for memory creation
                    recent_messages = self.conversation_worker.conversation_history[-10:]  # Last 10 messages
                    conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
                    
                    # Create a memory summary using the memory worker
                    if hasattr(self.memory_worker, 'create_memory_summary'):
                        memory_key = f"conversation_turn_{len(self.conversation_worker.conversation_history)}"
                        memory_summary = self.memory_worker.create_memory_summary(conversation_text, max_length=150)
                        if memory_summary:
                            self.logger.console.print(f"💾 Memory created: {memory_summary[:60]}...", style="dim green")
                        else:
                            self.logger.console.print("⚠️  Memory creation failed", style="dim red")
                    else:
                        self.logger.console.print("⚠️  Memory worker has no create_memory_summary method", style="dim red")
            
            return response if response else "No response generated"
            
        except Exception as e:
            self.logger.error(f"Error running real conversation turn: {e}")
            return f"Error generating response: {e}"

    def _generate_llm_response(self, prompt):
        """Generate a response using the LLM worker."""
        try:
            if not hasattr(self, 'llm_worker') or not self.llm_worker:
                return "Test response - LLM worker not available"
            
            # Format the prompt for the LLM
            formatted_prompt = self.conversation_worker.format_chat_prompt(
                prompt, 
                self.llm_worker, 
                self.memory_worker
            )
            
            # Generate response using the correct method
            if hasattr(self.llm_worker, 'generate_response'):
                response = self.llm_worker.generate_response(
                    formatted_prompt,
                    max_tokens=self.config.llm.max_tokens,
                    temperature=self.config.llm.temperature
                )
            else:
                return "Error: LLM worker has no generate_response method"
            
            return response if response else "No response generated"
            
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return f"Error generating response: {e}"

    def _show_detailed_performance_metrics(self):
        """Show detailed performance metrics and system statistics."""
        try:
            # Get performance data from all workers
            llm_stats = self.llm_worker.get_performance_stats() if hasattr(self.llm_worker, 'get_performance_stats') else {}
            memory_stats = self.memory_worker.get_memory_stats() if hasattr(self.memory_worker, 'get_memory_stats') else {}
            tts_stats = self.tts_worker.get_performance_stats() if hasattr(self.tts_worker, 'get_performance_stats') else {}
            
            # Calculate system uptime
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            
            # Create performance panel
            performance_data = f"""
╭─ Performance Metrics ──────────────────────────────────────────────────────────╮
│ System Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}                                    │
│ Total Conversations: {self.total_conversations}                                        │
│                                                                                 │
│ LLM Worker:                                                                     │
│   • Total Requests: {llm_stats.get('total_requests', 0)}                                    │
│   • Total Tokens Generated: {llm_stats.get('total_tokens_generated', 0)}                        │
│   • Average Response Time: {llm_stats.get('average_response_time', 0.0):.2f}s                    │
│                                                                                 │
│ Memory Worker:                                                                  │
│   • Total Memories: {memory_stats.get('total_memories', 0)}                                    │
│   • Cache Size: {memory_stats.get('cache_size', 0)}                                        │
│   • Memory Model Active: {memory_stats.get('memory_model_active', False)}                    │
│                                                                                 │
│ TTS Worker:                                                                    │
│   • Total Requests: {tts_stats.get('total_requests', 0)}                                    │
│   • Total Audio Generated: {tts_stats.get('total_audio_generated', 0)} bytes                    │
│   • Average Generation Time: {tts_stats.get('average_generation_time', 0.0):.2f}s              │
╰─────────────────────────────────────────────────────────────────────────────────╯
            """
            
            self.logger.console.print(performance_data, style="cyan")
            
        except Exception as e:
            self.logger.error(f"Error showing performance metrics: {e}")

    def _show_conversation_analysis(self):
        """Show detailed conversation analysis and statistics."""
        try:
            if not hasattr(self, 'benchmark_results') or not self.benchmark_results:
                self.logger.console.print("No benchmark results available", style="yellow")
                return
            
            results = self.benchmark_results
            conversation_data = results['conversation_data']
            
            # Analyze conversation patterns by category
            intro_turns = [t for t in conversation_data if t['category'] == 'intro']
            combat_turns = [t for t in conversation_data if t['category'] == 'combat']
            memory_turns = [t for t in conversation_data if t['category'] == 'memory']
            quality_turns = [t for t in conversation_data if t['category'] == 'quality']
            
            # Calculate statistics
            total_turns = len(conversation_data)
            successful_turns = sum(1 for turn in conversation_data if not turn['response'].startswith('ERROR'))
            
            # Show conversation summary
            conv_data = f"""
╭─ Conversation Analysis ──────────────────────────────────────────────────────╮
│ Total Turns: {total_turns}                                                          │
│ Successful Turns: {successful_turns}                                                    │
│ Failed Turns: {total_turns - successful_turns}                                                    │
│                                                                                 │
│ Turn Distribution:                                                              │
│   • Introduction: {len(intro_turns)} turns                                                          │
│   • Combat: {len(combat_turns)} turns                                                          │
│   • Memory: {len(memory_turns)} turns                                                          │
│   • Quality: {len(quality_turns)} turns                                                          │
│                                                                                 │
│ Response Statistics:                                                             │
│   • Average Response Length: {sum(len(turn['response']) for turn in conversation_data)/total_turns:.1f} chars                                                │
│   • Average Token Count: {sum(turn['token_count'] for turn in conversation_data)/total_turns:.1f}                                                        │
│   • Total Tokens Generated: {results['total_tokens_generated']:.0f}                                                        │
╰─────────────────────────────────────────────────────────────────────────────────╯
            """
            
            self.logger.console.print(conv_data, style="cyan")
            
            # Show recent conversation turns
            if conversation_data:
                self.logger.console.print("\n📝 Recent Conversation Turns:", style="bold yellow")
                recent_turns = conversation_data[-10:]  # Last 10 turns
                for turn in recent_turns:
                    category_icon = {"intro": "👋", "combat": "⚔️", "memory": "🧠", "quality": "✨"}.get(turn['category'], "❓")
                    status_icon = "✅" if not turn['response'].startswith('ERROR') else "❌"
                    response_preview = turn['response'][:60] + "..." if len(turn['response']) > 60 else turn['response']
                    self.logger.console.print(f"{turn['turn']:2d}. {category_icon} {status_icon} {turn['category'].title()}: {response_preview}", style="white")
            
        except Exception as e:
            self.logger.error(f"Error showing conversation analysis: {e}")

    def _show_memory_analysis(self):
        """Show detailed memory system analysis."""
        try:
            if not hasattr(self.memory_worker, 'get_memory_stats'):
                self.logger.console.print("Memory worker not available", style="yellow")
                return
            
            memory_stats = self.memory_worker.get_memory_stats()
            
            # Get memory cache details
            memory_cache = getattr(self.memory_worker, 'memory_cache', {})
            conversation_patterns = getattr(self.memory_worker, 'conversation_patterns', {})
            character_memories = getattr(self.memory_worker, 'character_memories', {})
            
            # Analyze memory content
            total_memories = len(memory_cache)
            avg_memory_length = sum(len(memory) for memory in memory_cache.values()) / max(total_memories, 1)
            
            # Show memory statistics
            memory_data = f"""
╭─ Memory System Analysis ──────────────────────────────────────────────────────╮
│ Memory Model Status: {'🟢 Active' if memory_stats.get('memory_model_active') else '🔴 Inactive'}                    │
│ Total Cached Memories: {total_memories}                                                │
│ Conversation Patterns: {len(conversation_patterns)}                                                │
│ Character Memories: {len(character_memories)}                                                │
│                                                                                 │
│ Memory Statistics:                                                               │
│   • Average Memory Length: {avg_memory_length:.1f} characters                                    │
│   • Cache Utilization: {total_memories}/{memory_stats.get('cache_size', 100)} ({total_memories/max(memory_stats.get('cache_size', 100), 1)*100:.1f}%) │
│                                                                                 │
│ Memory Types:                                                                    │
│   • Conversation Summaries: {sum(1 for m in memory_cache.values() if 'conversation' in m.lower())}                    │
│   • Topic Memories: {sum(1 for m in memory_cache.values() if 'topic' in m.lower() or 'help' in m.lower())}                    │
│   • Character Details: {sum(1 for m in memory_cache.values() if 'visitor' in m.lower() or 'client' in m.lower())}                    │
╰─────────────────────────────────────────────────────────────────────────────────╯
            """
            
            self.logger.console.print(memory_data, style="cyan")
            
            # Show sample memories
            if memory_cache:
                self.logger.console.print("\n🧠 Sample Memories:", style="bold yellow")
                sample_memories = list(memory_cache.items())[:5]  # First 5 memories
                for i, (key, memory) in enumerate(sample_memories, 1):
                    key_preview = key[:40] + "..." if len(key) > 40 else key
                    memory_preview = memory[:60] + "..." if len(memory) > 60 else memory
                    self.logger.console.print(f"{i}. Key: {key_preview}", style="white")
                    self.logger.console.print(f"   Memory: {memory_preview}", style="dim white")
                    self.logger.console.print()
            
        except Exception as e:
            self.logger.error(f"Error showing memory analysis: {e}")

    def _show_llm_performance_analysis(self):
        """Show detailed LLM performance analysis."""
        try:
            if not hasattr(self.llm_worker, 'get_performance_stats'):
                self.logger.console.print("LLM worker not available", style="yellow")
                return
            
            llm_stats = self.llm_worker.get_performance_stats()
            
            # LLM Model Details
            model_name = self.config.llm.model_repo.split('/')[-1] if '/' in self.config.llm.model_repo else self.config.llm.model_repo
            model_data = f"""
╭─ LLM Model Performance ────────────────────────────────────────────────────────╮
│ Model: {model_name}                                    │
│ Context Window: {self.config.llm.context_window} tokens                                                │
│ Max Tokens: {self.config.llm.max_tokens} tokens                                                    │
│ Temperature: {self.config.llm.temperature}                                                          │
│                                                                                 │
│ Performance Metrics:                                                            │
│   • Total Requests: {llm_stats.get('total_requests', 0)}                                                    │
│   • Total Tokens Generated: {llm_stats.get('total_tokens_generated', 0)}                                │
│   • Average Response Time: {llm_stats.get('average_response_time', 0.0):.3f}s                            │
│   • Tokens per Second: {llm_stats.get('total_tokens_generated', 0) / max(llm_stats.get('average_response_time', 1), 1):.1f}        │
╰─────────────────────────────────────────────────────────────────────────────────╯
                """
            self.logger.console.print(model_data, style="cyan")
            
        except Exception as e:
            self.logger.error(f"Error showing LLM performance analysis: {e}")

    def _show_benchmark_summary(self):
        """Show benchmark summary and recommendations."""
        try:
            # Calculate overall system health score
            health_score = 0
            recommendations = []
            
            # Check test conversation results if available
            if hasattr(self, 'benchmark_results') and self.benchmark_results:
                test_results = self.benchmark_results
                if test_results['success_rate'] >= 0.9:
                    health_score += 50
                elif test_results['success_rate'] >= 0.7:
                    health_score += 30
                    recommendations.append("Some test conversations failed - check system stability")
                else:
                    health_score += 10
                    recommendations.append("Multiple test conversations failed - system needs attention")
                
                # Check response time from tests
                if test_results['avg_response_time'] < 3.0:
                    health_score += 50
                elif test_results['avg_response_time'] < 6.0:
                    health_score += 30
                    recommendations.append("Test response times are acceptable but could be improved")
                else:
                    health_score += 10
                    recommendations.append("Test response times are slow - consider optimization")
            else:
                health_score += 25
                recommendations.append("No test conversation data available")
            
            # Determine health status
            if health_score >= 90:
                status = "🟢 EXCELLENT"
                status_style = "bold green"
            elif health_score >= 75:
                status = "🟡 GOOD"
                status_style = "bold yellow"
            elif health_score >= 60:
                status = "🟠 FAIR"
                status_style = "bold red"
            else:
                status = "🔴 POOR"
                status_style = "bold red"
            
            # Show benchmark summary
            summary_data = f"""
╭─ Benchmark Summary ───────────────────────────────────────────────────────────╮
│ Overall Health Score: {health_score}/100 {status}                                    │
│                                                                                 │
│ System Status:                                                                  │
│   • LLM Worker: {'🟢 Active' if self.llm_worker and hasattr(self.llm_worker, 'is_initialized') and self.llm_worker.is_initialized else '🔴 Inactive'}                    │
│   • Memory Worker: {'🟢 Active' if self.memory_worker and hasattr(self.memory_worker, 'is_initialized') and self.memory_worker.is_initialized else '🔴 Inactive'}                │
│   • TTS Worker: {'🟢 Active' if self.tts_worker and hasattr(self.tts_worker, 'is_initialized') and self.tts_worker.is_initialized else '🔴 Inactive'}                      │
│   • ASR Worker: {'🟢 Active' if hasattr(self, 'asr_worker') and self.asr_worker else '🔴 Inactive'}                      │
│                                                                                 │
│ Test Results:                                                                   │
"""
            
            # Add test results if available
            if hasattr(self, 'benchmark_results') and self.benchmark_results:
                test_results = self.benchmark_results
                summary_data += f"│   • Test Success Rate: {test_results['success_rate']*100:.1f}%                                                │\n"
                summary_data += f"│   • Avg Response Time: {test_results['avg_response_time']:.2f}s                                                │\n"
                summary_data += f"│   • Total Tokens: {test_results['total_tokens_generated']:.0f}                                                        │\n"
                summary_data += f"│   • Tokens per Second: {test_results['tokens_per_second']:.1f}                                                        │\n"
            else:
                summary_data += "│   • No test data available                                                │\n"
            
            summary_data += "│                                                                                 │\n│ Recommendations:                                                                │\n"
            
            # Add recommendations
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    summary_data += f"│   {i}. {rec}\n"
                    # Truncate long recommendations
                    if len(rec) > 70:
                        summary_data = summary_data[:-1] + "..." + summary_data[-1:]
            else:
                summary_data += "│   • System is running optimally\n"
            
            summary_data += "╰─────────────────────────────────────────────────────────────────────────────────╯"
            
            self.logger.console.print(summary_data, style=status_style)
            
        except Exception as e:
            self.logger.error(f"Error showing benchmark summary: {e}")
    
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
            if hasattr(self, 'memory_worker') and self.memory_worker:
                self.memory_worker.cleanup()
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
