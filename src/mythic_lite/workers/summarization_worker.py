import threading
import time
from typing import Optional, Any, Dict, List
from llama_cpp import Llama

# Remove circular imports - don't import from core
# from .config import get_config
# from .model_manager import ensure_model
from ..utils.logger import get_logger


class SummarizationWorker:
    """Worker class for handling text summarization"""
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        if config is None:
            # Create a minimal config if none provided
            self.config = type('Config', (), {
                'summarization': type('SummarizationConfig', (), {
                    'model_repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
                    'model_filename': 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'
                })(),
                'debug_mode': False
            })()
        
        self.logger = get_logger("summarization-worker")
        
        self.summarizer = None
        self.is_initialized = False
        self.initialization_error = None
        self.is_enabled = False
        
        self.logger.debug("SummarizationWorker initialized")
        
    def initialize(self) -> bool:
        """Initialize the summarization model."""
        try:
            self.logger.info("Attempting to load Llama-3.1-8B-Instruct summarization model...")
            
            # Use lazy import to avoid circular dependencies
            from ..core.model_manager import ensure_model
            
            # Ensure model is downloaded
            model_path = ensure_model(
                "summarization",
                self.config.summarization.model_repo,
                self.config.summarization.model_filename
            )
            
            if not model_path:
                raise Exception("Failed to download summarization model")
            
            # Initialize model with configuration
            if not model_path.exists():
                raise Exception(f"Model file not found: {model_path}")
            
            self.summarizer = Llama(
                model_path=str(model_path),
                verbose=self.config.debug_mode,
                n_ctx=256  # Smaller context for summarization
            )
            
            self.is_initialized = True
            self.initialization_error = None
            
            self.logger.success("Summarization model initialized successfully!")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.warning(f"Model loading failed: {e}")
            self.logger.info("Falling back to simple text extraction mode")
            self.is_initialized = False
            return False

    
    def test_summarization_model(self):
        """Test the summarization model with a simple prompt to ensure it's working"""
        if not self.summarizer:
            return False
        
        try:
            # Test prompt using Llama instruction format - simplified for faster response
            test_prompt = """<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Summarize this scenario from your perspective: "Visitor needs help with a problem."<|eot_id|><|start_header_id|>assistant<|end_header_id|>

From my perspective, this scenario involves: """
            
            self.logger.debug(f"[DEBUG] Test prompt: {test_prompt}")
            
            # Test with timeout protection (cross-platform)
            result = [None]
            exception = [None]
            
            def test_model():
                try:
                    self.logger.debug("[DEBUG] Calling summarizer for test...")
                    response = self.summarizer(
                        test_prompt,
                        max_tokens=20,  # Very short for test
                        temperature=0.0,  # Zero temperature to prevent hallucination
                        stop=["<|eot_id|>"]
                    )
                    self.logger.debug(f"[DEBUG] Got test response: {response}")
                    result[0] = response
                except Exception as e:
                    self.logger.debug(f"[DEBUG] Test exception: {e}")
                    exception[0] = e
            
            # Start test in separate thread
            test_thread = threading.Thread(target=test_model)
            test_thread.daemon = True
            test_thread.start()
            
            self.logger.debug("[DEBUG] Test thread started, waiting for response...")
            
            # Wait for completion or timeout (20 seconds for initialization - larger model needs more time)
            test_thread.join(timeout=20.0)
            
            if test_thread.is_alive():
                self.logger.warning("Model test timed out - model may be slow to start")
                return False
            
            if exception[0]:
                raise exception[0]
            
            self.logger.debug(f"[DEBUG] Test result: {result[0]}")
            
            # Check if we got a valid response - be more flexible with response formats
            if result[0]:
                self.logger.debug("[DEBUG] Test passed - got response")
                return True
            else:
                self.logger.debug("[DEBUG] Test failed - no response")
                return False
                
        except Exception as e:
            self.logger.error(f"Model test failed: {e}")
            return False
    
    def create_ai_summary(self, text, max_length=100):
        """Use the Llama model to create intelligent summaries"""
        if not self.is_enabled or not self.summarizer or not text:
            return None
        
        try:
            # Validate the summarization model is still working
            if not hasattr(self.summarizer, 'generate') and not hasattr(self.summarizer, '__call__'):
                self.logger.warning("Summarization model appears to be corrupted, disabling...")
                self.summarizer = None
                self.is_enabled = False
                return None
            
            # Create a prompt using Llama instruction format - from Mythic's perspective
            summary_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are Mythic, a 19th century mercenary AI. Summarize this conversation as a scenario from your perspective - what situation the visitor is in, what they need help with, and how you're assisting them. Focus on the practical scenario and context. Keep summaries under {max_length} characters. Write as if you're recalling a client interaction.<|eot_id|><|start_header_id|>user<|end_header_id|>

Summarize this conversation scenario from your perspective as Mythic:

{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

From my perspective, this scenario involves: """
            
            # Generate summary with timeout protection (cross-platform)
            result = [None]
            exception = [None]
            
            def generate_summary():
                try:
                    response = self.summarizer(
                        summary_prompt,
                        max_tokens=80,
                        temperature=0.0,  # Zero temperature to prevent hallucination
                        stop=["<|eot_id|>"]
                    )
                    result[0] = response
                except Exception as e:
                    exception[0] = e
            
            # Start generation in separate thread
            summary_thread = threading.Thread(target=generate_summary)
            summary_thread.daemon = True
            summary_thread.start()
            
            # Wait for completion or timeout (15 seconds for reliable response - larger model needs more time)
            summary_thread.join(timeout=15.0)
            
            if summary_thread.is_alive():
                self.logger.warning("Summarization timed out, falling back to simple summary")
                return self._create_simple_summary(text, "", max_length)
            
            self.logger.debug(f"[DEBUG] Thread completed, result: {result[0]}")
            
            if exception[0]:
                raise exception[0]
            
            self.logger.debug(f"[create_ai_summary] Raw response: {result[0]} (type: {type(result[0])})")
            
            if result[0] is None:
                self.logger.warning("No response generated from summarization model")
                return None
            elif isinstance(result[0], dict) and 'choices' in result[0]:
                summary = result[0]['choices'][0].get('text', '').strip()
                self.logger.debug(f"[DEBUG] Raw text from choices: '{summary}'")
            elif hasattr(result[0], 'choices'):
                summary = result[0].choices[0].text.strip() if result[0].choices else ''
                self.logger.debug(f"[DEBUG] Raw text from choices: '{summary}'")
            else:
                self.logger.warning(f"[create_ai_summary] Unexpected response format: {type(result[0])} - {result[0]}")
                summary = str(result[0]).strip()
            
            # Clean up the summary
            summary = summary.replace('<|eot_id|>', '').strip()
            self.logger.debug(f"[DEBUG] After cleaning: '{summary}'")
            
            # Remove common unwanted prefixes
            unwanted_prefixes = ['summary:', 'summary', 'summarize:', 'summarize']
            for prefix in unwanted_prefixes:
                if summary.lower().startswith(prefix.lower()):
                    summary = summary[len(prefix):].strip()
                    break
            
            # Remove any remaining artifacts
            summary = summary.replace('Summary:', '').replace('summary:', '').strip()
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            # Only return if we have meaningful content
            if summary and len(summary.strip()) > 5:
                return summary
            return None
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            # If we get a critical error, disable the summarization model
            if "access violation" in str(e).lower() or "segmentation fault" in str(e).lower():
                self.logger.warning("Critical summarization error detected, disabling model permanently...")
                self.summarizer = None
                self.is_enabled = False
            return None
    
    def create_topic_summary(self, topic, relevant_messages, max_length=150):
        """Create an intelligent summary of a specific conversation topic using Llama"""
        if not self.is_enabled or not self.summarizer or not relevant_messages:
            return None
        
        try:
            # Validate the summarization model is still working
            if not hasattr(self.summarizer, 'generate') and not hasattr(self.summarizer, '__call__'):
                self.logger.warning("Summarization model appears to be corrupted, disabling...")
                self.summarizer = None
                self.is_enabled = False
                return None
            
            # Prepare text for topic-specific summarization
            topic_text = f"Topic: {topic}\n\n"
            for msg in relevant_messages[-8:]:  # Last 8 messages for context
                role = "Visitor" if msg['role'] == 'user' else "Mythic"
                topic_text += f"{role}: {msg['content']}\n"
            
            # Create a focused summary prompt using Llama format - from Mythic's perspective
            summary_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are Mythic, a 19th century mercenary AI. Create focused summaries of specific conversation topics from your perspective, as if you're recalling what you and the visitor discussed about this topic. Focus on what was discussed and key points mentioned. Keep it under {max_length} characters. Write in a conversational, personal tone.<|eot_id|><|start_header_id|>user<|end_header_id|>

Summarize from your perspective what we discussed about "{topic}". Keep it under {max_length} characters:

{topic_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

From my perspective, we discussed: """
            
            # Generate topic summary with timeout protection (cross-platform)
            result = [None]
            exception = [None]
            
            def generate_topic_summary():
                try:
                    response = self.summarizer(
                        summary_prompt,
                        max_tokens=80,
                        temperature=0.0,  # Zero temperature to prevent hallucination
                        stop=["<|eot_id|>"]
                    )
                    result[0] = response
                except Exception as e:
                    exception[0] = e
            
            # Start generation in separate thread
            topic_thread = threading.Thread(target=generate_topic_summary)
            topic_thread.daemon = True
            topic_thread.start()
            
            # Wait for completion or timeout (15 seconds for reliable response - larger model needs more time)
            topic_thread.join(timeout=15.0)
            
            if topic_thread.is_alive():
                self.logger.warning("Topic summarization timed out, falling back to simple summary")
                return self._create_simple_summary(topic_text, "", max_length)
            
            self.logger.debug(f"[DEBUG] Thread completed, result: {result[0]}")
            
            if exception[0]:
                raise exception[0]
            
            self.logger.debug(f"[create_topic_summary] Raw response: {result[0]} (type: {type(result[0])})")
            
            if result[0] is None:
                self.logger.warning("No response generated from summarization model")
                return None
            elif isinstance(result[0], dict) and 'choices' in result[0]:
                summary = result[0]['choices'][0].get('text', '').strip()
                self.logger.debug(f"[DEBUG] Raw text from choices: '{summary}'")
            elif hasattr(result[0], 'choices'):
                summary = result[0].choices[0].text.strip() if result[0].choices else ''
                self.logger.debug(f"[DEBUG] Raw text from choices: '{summary}'")
            else:
                self.logger.warning(f"[create_topic_summary] Unexpected response format: {type(result[0])} - {result[0]}")
                summary = str(result[0]).strip()
            
            # Clean up the summary
            summary = summary.replace('<|eot_id|>', '').strip()
            self.logger.debug(f"[DEBUG] After cleaning: '{summary}'")
            
            # Remove common unwanted prefixes
            unwanted_prefixes = ['summary:', 'summary', 'summarize:', 'summarize']
            for prefix in unwanted_prefixes:
                if summary.lower().startswith(prefix.lower()):
                    summary = summary[len(prefix):].strip()
                    break
            
            # Remove any remaining artifacts
            summary = summary.replace('Summary:', '').replace('summary:', '').strip()
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            # Only return if we have meaningful content
            if summary and len(summary.strip()) > 5:
                return summary
            return None
            
        except Exception as e:
            self.logger.error(f"Topic summarization failed: {e}")
            # If we get a critical error, disable the summarization model
            if "access violation" in str(e).lower() or "segmentation fault" in str(e).lower():
                self.logger.warning("Critical topic summarization error detected, disabling model permanently...")
                self.summarizer = None
                self.is_enabled = False
            return None
    
    def reload_model(self):
        """Attempt to reload the summarization model if it was disabled due to errors"""
        if self.summarizer is not None and self.is_enabled:
            self.logger.info("Summarization model is already loaded and enabled.")
            return True
        
        try:
            self.logger.info("Attempting to reload Llama-3.1-8B-Instruct summarization model...")
            
            # Ensure model is downloaded
            model_path = ensure_model(
                "summarization",
                self.config.summarization.model_repo,
                self.config.summarization.model_filename
            )
            
            if not model_path:
                raise Exception("Failed to download summarization model")
            
            # For local GGUF files, use Llama() directly instead of from_pretrained()
            # model_path already includes the filename, so use it directly
            if not model_path.exists():
                raise Exception(f"Model file not found: {model_path}")
            
            self.summarizer = Llama(
                model_path=str(model_path),
                verbose=self.config.debug_mode
            )
            
            if self.test_summarization_model():
                self.logger.success("Summarization model reloaded successfully!")
                self.is_enabled = True
                return True
            else:
                self.logger.warning("Reloaded model failed test, keeping disabled...")
                self.summarizer = None
                self.is_enabled = False
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to reload summarization model: {e}")
            self.summarizer = None
            self.is_enabled = False
            return False
    
    def get_status(self) -> str:
        """Get the status of the summarization worker."""
        if self.is_initialized and self.is_enabled:
            return f"Summarization: {self.config.summarization.model_repo} (AI Model Active)"
        elif self.is_initialized and not self.is_enabled:
            return f"Summarization: Simple Text Extraction Mode (AI Model Unavailable)"
        elif self.initialization_error:
            return f"Summarization: Failed to initialize - {self.initialization_error}"
        else:
            return "Summarization: Not initialized"
    
    def create_continuous_summary(self, conversation_text, current_summary="", max_length=120):
        """Create a continuous summary that balances speed and coverage
        
        This method creates incremental summaries that build upon previous summaries,
        providing a balance between summarization speed and comprehensive coverage.
        Falls back to simple text extraction if AI summarization fails.
        """
        if not self.is_enabled or not self.summarizer:
            # Fallback to simple text extraction
            return self._create_simple_summary(conversation_text, current_summary, max_length)
        
        try:
            # If we have a previous summary, create an incremental update
            if current_summary:
                prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are Mythic, a 19th century mercenary AI. Update your existing scenario summary with new developments. Write from your perspective as if you're recalling a client interaction that's evolving. Keep the updated summary under {max_length} characters. Focus on how the situation is developing.<|eot_id|><|start_header_id|>user<|end_header_id|>

Update your existing scenario summary with new conversation content:

Your Previous Summary: {current_summary}

New Conversation: {conversation_text}

Updated Summary from your perspective:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

From my perspective, this scenario is now: """
            else:
                # First-time summary
                prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are Mythic, a 19th century mercenary AI. Summarize this conversation as a scenario from your perspective - what situation the visitor is in, what they need help with, and how you're assisting them. Focus on the practical scenario and context. Keep summaries under {max_length} characters. Write as if you're recalling a new client interaction.<|eot_id|><|start_header_id|>user<|end_header_id|>

Summarize this conversation scenario from your perspective as Mythic:

{conversation_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

From my perspective, this scenario involves: """
            
            # Generate incremental summary with timeout protection
            result = [None]
            exception = [None]
            
            def generate_incremental_summary():
                try:
                    self.logger.debug(f"[DEBUG] Calling summarizer with prompt: {prompt[:100]}...")
                    response = self.summarizer(
                        prompt,
                        max_tokens=80,
                        temperature=0.0,  # Zero temperature to prevent hallucination
                        stop=["<|eot_id|>"]
                    )
                    self.logger.debug(f"[DEBUG] Got response: {response}")
                    result[0] = response
                except Exception as e:
                    self.logger.debug(f"[DEBUG] Exception in generate_incremental_summary: {e}")
                    exception[0] = e
            
            # Start generation in separate thread
            summary_thread = threading.Thread(target=generate_incremental_summary)
            summary_thread.daemon = True
            summary_thread.start()
            
            # Wait for completion or timeout (15 seconds for reliable response - larger model needs more time)
            summary_thread.join(timeout=15.0)
            
            if summary_thread.is_alive():
                self.logger.warning("Continuous summarization timed out, falling back to simple summary")
                return self._create_simple_summary(conversation_text, current_summary, max_length)
            
            self.logger.debug(f"[DEBUG] Thread completed, result: {result[0]}")
            
            if exception[0]:
                raise exception[0]
            
            self.logger.debug(f"[create_continuous_summary] Raw response: {result[0]} (type: {type(result[0])})")
            
            if result[0] is None:
                self.logger.warning("No response generated from summarization model")
                return None
            elif isinstance(result[0], dict) and 'choices' in result[0]:
                summary = result[0]['choices'][0].get('text', '').strip()
                self.logger.debug(f"[DEBUG] Raw text from choices: '{summary}'")
            elif hasattr(result[0], 'choices'):
                summary = result[0].choices[0].text.strip() if result[0].choices else ''
                self.logger.debug(f"[DEBUG] Raw text from choices: '{summary}'")
            else:
                self.logger.warning(f"[create_continuous_summary] Unexpected response format: {type(result[0])} - {result[0]}")
                summary = str(result[0]).strip()
            
            # Clean up the summary
            summary = summary.replace('<|eot_id|>', '').strip()
            self.logger.debug(f"[DEBUG] After cleaning: '{summary}'")
            
            # Remove common unwanted prefixes
            unwanted_prefixes = ['summary:', 'summary', 'summarize:', 'summarize']
            for prefix in unwanted_prefixes:
                if summary.lower().startswith(prefix.lower()):
                    summary = summary[len(prefix):].strip()
                    break
            
            # Remove any remaining artifacts
            summary = summary.replace('Summary:', '').replace('summary:', '').strip()
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            # Only return if we have meaningful content
            if summary and len(summary.strip()) > 5:
                return summary
            return None
            
        except Exception as e:
            self.logger.error(f"Continuous summarization failed: {e}")
            return None
    
    def _create_simple_summary(self, conversation_text, current_summary="", max_length=120):
        """Create a simple summary using text extraction when AI summarization is not available"""
        try:
            # Parse conversation to understand the scenario
            lines = conversation_text.split('\n')
            visitor_messages = []
            mythic_messages = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Visitor:'):
                    content = line.replace('Visitor:', '').strip()
                    if content and len(content) > 3:
                        visitor_messages.append(content)
                elif line.startswith('Mythic:'):
                    content = line.replace('Mythic:', '').strip()
                    if content and len(content) > 3:
                        mythic_messages.append(content)
            
            # Create a scenario-based summary from Mythic's perspective
            if visitor_messages and mythic_messages:
                # Identify the main scenario/topic
                if current_summary and current_summary != "Conversation in progress...":
                    # Update existing scenario
                    recent_visitor = visitor_messages[-1][:40] if visitor_messages else "recent topics"
                    summary = f"Continuing our scenario about {current_summary[:30]}... The visitor just mentioned: {recent_visitor}"
                else:
                    # New scenario
                    first_visitor = visitor_messages[0][:50] if visitor_messages else "their needs"
                    summary = f"New visitor arrived seeking {first_visitor}. I'm helping them with their situation."
                
                if len(summary) > max_length:
                    summary = summary[:max_length-3] + "..."
                return summary
            
            # If no clear conversation structure, create a basic scenario summary
            if current_summary and current_summary != "Conversation in progress...":
                return f"Continuing our previous scenario about {current_summary[:max_length-30]}..."
            else:
                return "New conversation scenario beginning..."
                
        except Exception as e:
            self.logger.debug(f"Simple summary creation failed: {e}")
            return "Our conversation scenario continues..."
    
    def cleanup(self):
        """Clean up resources"""
        if self.summarizer:
            try:
                self.summarizer = None
                self.is_initialized = False
                self.is_enabled = False
                self.logger.info("Summarization worker cleaned up")
            except Exception as e:
                self.logger.error(f"Error during summarization cleanup: {e}")
