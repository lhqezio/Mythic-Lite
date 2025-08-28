import time
import re
from typing import Optional, Any, Dict, List
from .config import get_config
from ..utils.logger import get_logger


class ConversationWorker:
    """Worker class for handling conversation management and memory"""
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config or get_config()
        self.logger = get_logger("conversation-worker")
        
        self.conversation_history = []
        self.conversation_summary = ""
        self.debug_mode = False
        
        # Conversation memory settings from configuration
        self.max_conversation_length = self.config.conversation.max_conversation_length
        self.max_tokens_per_message = self.config.conversation.max_tokens_per_message
        
        # System prompt for Mythic character (shortened for small context)
        self.system_prompt = """<|system|>
You are MYTHIC, a fierce 19th-century female mercenary. Tough, practical, loyal. Use Victorian expressions: "Bloody hell," "By Jove," "mate." Stay in character as a real mercenary.
</s>"""
        
        self.logger.debug("ConversationWorker initialized")
    
    def format_chat_prompt(self, user_input, llm_worker, summarization_worker=None):
        """Format the conversation as a proper chat prompt for the LLM"""
        # Start with system prompt
        prompt = self.system_prompt
        
        # Add conversation summary if available (keep concise for small context)
        if self.conversation_summary:
            prompt += f"\n<|system|>\nContext: {self.conversation_summary}</s>"
        
        # Add conversation history (keep minimal context for small model)
        recent_messages = self.conversation_history[-6:]  # Last 6 messages to fit context
        for message in recent_messages:
            if message['role'] == 'user':
                prompt += f"\n<|user|>\n{message['content']}</s>"
            elif message['role'] == 'assistant':
                prompt += f"\n<|assistant|>\n{message['content']}</s>"
        
        # Add current user input
        prompt += f"\n<|user|>\n{user_input}</s>"
        
        # Add Mythic's response start (without newline to prevent extra spacing)
        prompt += "\n<|assistant|>"
        
        # Check prompt length for small context models
        if llm_worker:
            estimated_tokens = llm_worker.check_prompt_length(prompt)
            
            # Automatic prompt length management - seamless operation
            if estimated_tokens > 350:  # Leave buffer for response
                if self.debug_mode:
                    self.logger.debug(f"Prompt too long ({estimated_tokens} tokens), optimizing memory...")
                # Try continuous summarization first for seamless operation
                if summarization_worker and summarization_worker.is_enabled:
                    if self.continuous_summarize(summarization_worker):
                        # Reformat with updated summary
                        return self.format_chat_prompt(user_input, llm_worker, summarization_worker)
                
                # Fallback to force summarization if continuous fails
                self._force_summarization(summarization_worker)
                # Reformat with updated summary
                return self.format_chat_prompt(user_input, llm_worker, summarization_worker)
        
        return prompt
    
    def add_to_conversation(self, role, content, summarization_worker=None):
        """Add a message to the conversation history with memory management"""
        # Truncate very long messages to prevent memory issues
        if len(content) > self.max_tokens_per_message:
            content = content[:self.max_tokens_per_message] + "..."
        
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        
        # Automatic memory management - seamless and continuous
        if len(self.conversation_history) > self.max_conversation_length:
            # Always try continuous summarization first for seamless operation
            if summarization_worker and summarization_worker.is_enabled:
                if self.continuous_summarize(summarization_worker):
                    return  # Continuous summarization handled it automatically
            
            # Fallback to traditional summarization if continuous fails
            old_messages = self.conversation_history[:-8]  # Keep last 8 messages
            if old_messages:
                self._create_conversation_summary(old_messages, summarization_worker)
            
            # Keep recent messages and system context
            self.conversation_history = self.conversation_history[-8:]
    
    def _force_summarization(self, summarization_worker=None):
        """Force summarization when prompt gets too long"""
        if len(self.conversation_history) > 4:  # Only if we have enough messages
            # Keep only the last 4 messages and summarize the rest
            old_messages = self.conversation_history[:-4]
            if old_messages:
                self._create_conversation_summary(old_messages, summarization_worker)
            self.conversation_history = self.conversation_history[-4:]
    
    def _create_conversation_summary(self, old_messages, summarization_worker=None):
        """Create a summary of old conversation messages for memory management"""
        try:
            # Try AI summarization first if available
            if summarization_worker and summarization_worker.is_enabled:
                # Prepare text for AI summarization
                conversation_text = ""
                for msg in old_messages[-10:]:  # Last 10 messages for better context
                    role = "Visitor" if msg['role'] == 'user' else "Mythic"
                    conversation_text += f"{role}: {msg['content']}\n"
                
                if conversation_text:
                    # Try to create a continuous summary that builds on existing summary
                    ai_summary = summarization_worker.create_continuous_summary(
                        conversation_text, 
                        self.conversation_summary, 
                        max_length=150
                    )
                    if ai_summary and ai_summary.strip() and len(ai_summary.strip()) > 5:
                        # Validate that we got a meaningful summary
                        if not ai_summary.lower().startswith('summary:'):
                            self.conversation_summary = ai_summary.strip()
                            return
                        else:
                            # If we got "Summary:" prefix, extract the actual content
                            clean_summary = ai_summary.replace('Summary:', '').strip()
                            if clean_summary and len(clean_summary) > 5:
                                self.conversation_summary = clean_summary
                                return
            
            # Fallback to simple text extraction if AI summarization fails
            user_topics = []
            assistant_responses = []
            
            for msg in old_messages:
                if msg['role'] == 'user':
                    # Extract main topics from user messages
                    content = msg['content'].lower()
                    if len(content) > 20:  # Lower threshold for better coverage
                        # Simple topic extraction (first few words)
                        words = content.split()[:8]
                        user_topics.append(' '.join(words) + '...')
                    else:
                        user_topics.append(content)
                elif msg['role'] == 'assistant':
                    # Extract key points from assistant responses
                    content = msg['content'].lower()
                    if len(content) > 30:
                        # Simple key point extraction
                        sentences = content.split('.')[:2]
                        assistant_responses.append('. '.join(sentences) + '...')
                    else:
                        assistant_responses.append(content)
            
            # Create a concise summary for small context
            if user_topics or assistant_responses:
                summary_parts = []
                if user_topics:
                    summary_parts.append(f"Visitor: {', '.join(user_topics[-4:])}")  # Keep only 4 topics
                if assistant_responses:
                    summary_parts.append(f"Mythic: {', '.join(assistant_responses[-4:])}")  # Keep only 4 responses
                
                self.conversation_summary = " | ".join(summary_parts)
                
        except Exception as e:
            # If summary creation fails, just clear old summary
            if self.debug_mode:
                self.logger.debug(f"Summary creation failed: {e}")
            self.conversation_summary = ""
    
    def get_conversation_context(self, query="", summarization_worker=None):
        """Get relevant conversation context for better memory recall"""
        if not self.conversation_history:
            return "No previous conversation to recall, mate."
        
        # If query is provided, try to find relevant context
        if query:
            query_lower = query.lower()
            relevant_messages = []
            
            for msg in self.conversation_history[-10:]:  # Check last 10 messages
                if query_lower in msg['content'].lower():
                    relevant_messages.append(msg)
            
            if relevant_messages:
                # Try to create an intelligent topic summary if summarization model is available
                if summarization_worker and summarization_worker.is_enabled:
                    topic_summary = summarization_worker.create_topic_summary(query, relevant_messages)
                    if topic_summary:
                        return f"Topic: {query}\n\nAI Summary: {topic_summary}\n\nRelevant messages:\n" + "\n".join([
                            f"{'Visitor' if msg['role'] == 'user' else 'Mythic'}: {msg['content'][:80]}..."
                            for msg in relevant_messages[-3:]
                        ])
                
                # Fallback to simple context display
                return "Relevant context:\n" + "\n".join([
                    f"{'Visitor' if msg['role'] == 'user' else 'Mythic'}: {msg['content'][:80]}..."
                    for msg in relevant_messages[-3:]
                ])
        
        # General context
        recent_context = []
        for msg in self.conversation_history[-6:]:  # Last 6 messages
            if msg['role'] == 'user':
                role = "Visitor"
            elif msg['role'] == 'assistant':
                role = "Mythic"
            else:
                role = msg['role'].title()
            content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            recent_context.append(f"{role}: {content}")
        
        context = "Recent conversation:\n" + "\n".join(recent_context)
        
        if self.conversation_summary:
            context += f"\n\nPrevious summary: {self.conversation_summary}"
        
        return context
    
    def continuous_summarize(self, summarization_worker=None):
        """Perform seamless continuous summarization as conversation progresses
        
        This method automatically maintains optimal memory balance:
        - Creates incremental summaries that build on previous ones
        - Maintains context while adding new information
        - Works silently in the background for seamless operation
        """
        if len(self.conversation_history) > 6:  # Trigger earlier for seamless operation
            # Keep more recent messages for better context
            old_messages = self.conversation_history[:-6]
            if old_messages:
                # Use continuous summarization that builds on existing summary
                if summarization_worker and summarization_worker.is_enabled:
                    conversation_text = ""
                    for msg in old_messages[-8:]:  # Last 8 messages for context
                        role = "Visitor" if msg['role'] == 'user' else "Mythic"
                        conversation_text += f"{role}: {msg['content']}\n"
                    
                    if conversation_text:
                        # Create incremental summary silently
                        incremental_summary = summarization_worker.create_continuous_summary(
                            conversation_text,
                            self.conversation_summary,
                            max_length=120
                        )
                        if incremental_summary and incremental_summary.strip() and len(incremental_summary.strip()) > 5:
                            # Validate that we got a meaningful summary
                            if not incremental_summary.lower().startswith('summary:'):
                                self.conversation_summary = incremental_summary.strip()
                                # Only show in debug mode for seamless operation
                                if hasattr(self, 'debug_mode') and self.debug_mode:
                                    self.logger.debug(f"Memory optimized: {self.conversation_summary[:80]}...")
                            else:
                                # If we got "Summary:" prefix, extract the actual content
                                clean_summary = incremental_summary.replace('Summary:', '').strip()
                                if clean_summary and len(clean_summary) > 5:
                                    self.conversation_summary = clean_summary
                                    # Only show in debug mode for seamless operation
                                    if hasattr(self, 'debug_mode') and self.debug_mode:
                                        self.logger.debug(f"Memory optimized: {self.conversation_summary[:80]}...")
                
                # Remove old messages but keep more for context
                self.conversation_history = self.conversation_history[-6:]
                return True
        return False
    
    def clean_response(self, response: str) -> str:
        """Clean response text by removing artifacts and formatting."""
        if not response:
            return ""
        
        # Remove common LLM artifacts
        cleaned = response.strip()
        cleaned = cleaned.replace('</s>', '').replace('<s>', '')
        cleaned = cleaned.replace('<|endoftext|>', '')
        
        # Remove any remaining prompt artifacts
        if '<|' in cleaned:
            cleaned = cleaned[:cleaned.find('<|')].strip()
        
        return cleaned
    
    def validate_response(self, response: str) -> bool:
        """Validate if a response is meaningful and appropriate."""
        if not response or len(response.strip()) < 3:
            return False
        
        # Check for common error patterns
        error_patterns = [
            'error:', 'failed:', 'cannot', 'unable to', 'sorry, i cannot',
            'i am not able to', 'i cannot provide', 'i do not have access'
        ]
        
        response_lower = response.lower()
        for pattern in error_patterns:
            if pattern in response_lower:
                return False
        
        return True
    
    def extract_meaningful_content(self, response: str) -> str:
        """Extract meaningful content from a potentially corrupted response."""
        if not response:
            return ""
        
        # Try to find the start of meaningful content
        lines = response.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                # Skip lines that are just artifacts
                if not any(artifact in line.lower() for artifact in ['<|', '</s>', '<s>', 'error:', 'failed:']):
                    meaningful_lines.append(line)
        
        if meaningful_lines:
            return ' '.join(meaningful_lines)
        
        # Fallback: try to extract content before artifacts
        if '<|' in response:
            return response[:response.find('<|')].strip()
        
        return response.strip()
    
    def has_meaningful_content(self, response):
        """Check if response contains meaningful content beyond artifacts"""
        if not response:
            return False
        
        # Remove all known artifacts and check remaining content
        clean = response
        
        # Remove all prompt-related content
        artifacts_to_remove = [
            '<|user|>', '<|system|>', '<|assistant|>',
            '</s>', '<s>', '<|', '|>',
            'user:', 'system:', 'assistant:',
            'user|', 'system|', 'assistant|'
        ]
        
        for artifact in artifacts_to_remove:
            clean = clean.replace(artifact, '')
        
        # Remove any remaining incomplete tags
        clean = re.sub(r'<[^>]*', '', clean)
        clean = re.sub(r'[^>]*>', '', clean)
        
        # Clean up whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Check if we have meaningful content
        if len(clean) > 10:  # At least 10 characters of actual content
            # Check if it contains actual words, not just artifacts
            words = clean.split()
            if len(words) > 2:  # At least 3 words
                return True
        
        return False
    
    def mythic_greeting(self):
        """Display Mythic's dramatic entrance"""
        greetings = [
            "Well, well... looks like we have company. Mythic's the name, and survival's my game.",
            "Bloody hell, another soul seeking the wisdom of a mercenary. I'm Mythic, and I've seen things that would make your hair turn white.",
            "By Jove, a visitor! I'm Eleanor Blackwood, though most know me as Mythic. What brings you to seek counsel from a woman of my... profession?",
            "Ah, fresh meat—I mean, a new acquaintance! I'm Mythic, and I've got stories that would curl your toes. What's your business, mate?",
            "The shadows part, and here I stand. Mythic's my name, and I've walked through fire and blood to get where I am today."
        ]
        import random
        return random.choice(greetings)
    
    def get_conversation_summary(self):
        """Get the current conversation summary"""
        return self.conversation_summary
    
    def clear_conversation(self):
        """Clear the conversation history and summary"""
        self.conversation_history = []
        self.conversation_summary = ""
        self.logger.debug("Conversation history cleared.")
    
    def get_conversation_stats(self):
        """Get statistics about the conversation"""
        total_messages = len(self.conversation_history)
        user_messages = len([msg for msg in self.conversation_history if msg['role'] == 'user'])
        assistant_messages = len([msg for msg in self.conversation_history if msg['role'] == 'assistant'])
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'has_summary': bool(self.conversation_summary)
        }
    
    def force_summarize_now(self, summarization_worker=None):
        """Manually trigger summarization of current conversation history"""
        if len(self.conversation_history) > 4:
            old_messages = self.conversation_history[:-4]
            if old_messages:
                self._create_conversation_summary(old_messages, summarization_worker)
                self.conversation_history = self.conversation_history[-4:]
                if self.conversation_summary:
                    self.logger.debug(f"Manual summarization completed. Summary: {self.conversation_summary}")
                else:
                    self.logger.debug("Manual summarization completed but no summary was generated.")
                return True
        return False
    
    def test_summarization_system(self, summarization_worker=None):
        """Test the summarization system with sample conversation"""
        if not summarization_worker or not summarization_worker.is_enabled:
            return "Summarization worker not available or disabled"
        
        # Create test conversation
        test_messages = [
            {'role': 'user', 'content': 'Hello, how are you today?'},
            {'role': 'assistant', 'content': 'I am doing well, thank you for asking. How may I assist you?'},
            {'role': 'user', 'content': 'Can you tell me about the weather?'},
            {'role': 'assistant', 'content': 'I would be happy to help with weather information. What specific details are you looking for?'}
        ]
        
        try:
            # Test basic summarization
            conversation_text = ""
            for msg in test_messages:
                role = "Visitor" if msg['role'] == 'user' else "Mythic"
                conversation_text += f"{role}: {msg['content']}\n"
            
            # Test continuous summarization
            test_summary = summarization_worker.create_continuous_summary(
                conversation_text,
                "",
                max_length=100
            )
            
            if test_summary and len(test_summary.strip()) > 5:
                return f"Summarization test PASSED. Generated summary: {test_summary}"
            else:
                return f"Summarization test FAILED. Generated summary: '{test_summary}'"
                
        except Exception as e:
            return f"Summarization test ERROR: {e}"
