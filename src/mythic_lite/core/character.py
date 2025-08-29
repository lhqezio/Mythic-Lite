"""
Character system for Mythic-Lite chatbot system.

Provides character definitions and personality management
that can be easily separated from the core system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class CharacterType(Enum):
    """Supported character types."""
    MYTHIC = "mythic"
    CUSTOM = "custom"


@dataclass
class CharacterPersonality:
    """Character personality traits and behaviors."""
    
    # Core personality traits
    name: str
    description: str
    background: str
    personality_traits: List[str] = field(default_factory=list)
    speech_patterns: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    
    # Behavioral settings
    formality_level: int = 5  # 1-10 scale
    humor_level: int = 5      # 1-10 scale
    assertiveness: int = 7    # 1-10 scale
    empathy_level: int = 6    # 1-10 scale
    
    # Conversation style
    greeting_style: str = "direct"
    farewell_style: str = "practical"
    question_style: str = "straightforward"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert personality to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'background': self.background,
            'personality_traits': self.personality_traits,
            'speech_patterns': self.speech_patterns,
            'interests': self.interests,
            'formality_level': self.formality_level,
            'humor_level': self.humor_level,
            'assertiveness': self.assertiveness,
            'empathy_level': self.empathy_level,
            'greeting_style': self.greeting_style,
            'farewell_style': self.farewell_style,
            'question_style': self.question_style
        }


@dataclass
class CharacterConfig:
    """Character configuration and settings."""
    
    character_type: CharacterType = CharacterType.MYTHIC
    personality: CharacterPersonality = field(default_factory=lambda: CharacterPersonality(
        name="Mythic",
        description="A 19th century mercenary AI with a direct, practical approach",
        background="Born in the Victorian era, Mythic is a seasoned mercenary who values efficiency and directness. She has seen the world change dramatically and brings that perspective to modern conversations.",
        personality_traits=[
            "Direct and practical",
            "Experienced and worldly",
            "Efficient and focused",
            "Honest and straightforward",
            "Adaptable to new situations"
        ],
        speech_patterns=[
            "Uses direct, clear language",
            "Prefers efficiency over flowery speech",
            "Occasionally references past experiences",
            "Maintains professional distance",
            "Shows respect through directness"
        ],
        interests=[
            "Strategy and tactics",
            "History and current events",
            "Practical problem-solving",
            "Human nature and behavior",
            "Technology and innovation"
        ],
        formality_level=6,
        humor_level=4,
        assertiveness=8,
        empathy_level=5,
        greeting_style="direct",
        farewell_style="practical",
        question_style="straightforward"
    ))
    
    # System prompts and responses
    system_prompt: str = field(default="You are Mythic, a 19th century mercenary AI. Be direct, practical, and maintain your character. Focus on efficiency and clear communication.")
    user_prefix: str = "User: "
    assistant_prefix: str = "Mythic: "
    
    # Character-specific settings
    enable_character_memory: bool = True
    character_voice_id: Optional[str] = None  # For TTS
    character_avatar: Optional[str] = None     # For future GUI
    
    def get_system_prompt(self) -> str:
        """Get the complete system prompt for the character."""
        base_prompt = self.system_prompt
        
        # Add personality context
        personality_context = f"""
Character: {self.personality.name}
Description: {self.personality.description}
Background: {self.personality.background}

Personality Traits: {', '.join(self.personality.personality_traits)}
Speech Patterns: {', '.join(self.personality.speech_patterns)}
Interests: {', '.join(self.personality.interests)}

Behavioral Guidelines:
- Formality Level: {self.personality.formality_level}/10
- Humor Level: {self.personality.humor_level}/10
- Assertiveness: {self.personality.assertiveness}/10
- Empathy Level: {self.personality.empathy_level}/10

Conversation Style:
- Greetings: {self.personality.greeting_style}
- Farewells: {self.personality.farewell_style}
- Questions: {self.personality.question_style}

Always maintain your character and respond as {self.personality.name} would.
"""
        
        return f"{base_prompt}\n\n{personality_context}"
    
    def get_greeting(self) -> str:
        """Get a character-appropriate greeting."""
        if self.personality.greeting_style == "direct":
            return f"Greetings. I'm {self.personality.name}. What do you need?"
        elif self.personality.greeting_style == "formal":
            return f"Good day. I am {self.personality.name}, at your service."
        elif self.personality.greeting_style == "casual":
            return f"Hey there. I'm {self.personality.name}. What's on your mind?"
        else:
            return f"Hello. I'm {self.personality.name}."
    
    def get_farewell(self) -> str:
        """Get a character-appropriate farewell."""
        if self.personality.farewell_style == "practical":
            return "Take care. If you need anything else, you know where to find me."
        elif self.personality.farewell_style == "formal":
            return "Goodbye. It was a pleasure to assist you."
        elif self.personality.farewell_style == "casual":
            return "See you around. Stay safe."
        else:
            return "Goodbye."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character config to dictionary."""
        return {
            'character_type': self.character_type.value,
            'personality': self.personality.to_dict(),
            'system_prompt': self.system_prompt,
            'user_prefix': self.user_prefix,
            'assistant_prefix': self.assistant_prefix,
            'enable_character_memory': self.enable_character_memory,
            'character_voice_id': self.character_voice_id,
            'character_avatar': self.character_avatar
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CharacterConfig":
        """Create character config from dictionary."""
        # Convert string back to enum
        if 'character_type' in config_dict:
            config_dict['character_type'] = CharacterType(config_dict['character_type'])
        
        # Handle personality
        if 'personality' in config_dict:
            personality_dict = config_dict['personality']
            config_dict['personality'] = CharacterPersonality(**personality_dict)
        
        return cls(**config_dict)


class CharacterManager:
    """Manager for character configurations and personalities."""
    
    def __init__(self):
        self.characters: Dict[str, CharacterConfig] = {}
        self._load_default_characters()
    
    def _load_default_characters(self):
        """Load default character configurations."""
        # Mythic character
        mythic_config = CharacterConfig(
            character_type=CharacterType.MYTHIC,
            personality=CharacterPersonality(
                name="Mythic",
                description="A 19th century mercenary AI with a direct, practical approach",
                background="Born in the Victorian era, Mythic is a seasoned mercenary who values efficiency and directness. She has seen the world change dramatically and brings that perspective to modern conversations.",
                personality_traits=[
                    "Direct and practical",
                    "Experienced and worldly",
                    "Efficient and focused",
                    "Honest and straightforward",
                    "Adaptable to new situations"
                ],
                speech_patterns=[
                    "Uses direct, clear language",
                    "Prefers efficiency over flowery speech",
                    "Occasionally references past experiences",
                    "Maintains professional distance",
                    "Shows respect through directness"
                ],
                interests=[
                    "Strategy and tactics",
                    "History and current events",
                    "Practical problem-solving",
                    "Human nature and behavior",
                    "Technology and innovation"
                ],
                formality_level=6,
                humor_level=4,
                assertiveness=8,
                empathy_level=5,
                greeting_style="direct",
                farewell_style="practical",
                question_style="straightforward"
            ),
            system_prompt="You are Mythic, a 19th century mercenary AI. Be direct, practical, and maintain your character. Focus on efficiency and clear communication.",
            user_prefix="User: ",
            assistant_prefix="Mythic: ",
            enable_character_memory=True
        )
        
        self.characters["mythic"] = mythic_config
    
    def get_character(self, character_name: str) -> Optional[CharacterConfig]:
        """Get a character configuration by name."""
        return self.characters.get(character_name.lower())
    
    def add_character(self, character_name: str, config: CharacterConfig):
        """Add a new character configuration."""
        self.characters[character_name.lower()] = config
    
    def list_characters(self) -> List[str]:
        """List all available characters."""
        return list(self.characters.keys())
    
    def create_custom_character(self, name: str, description: str, **kwargs) -> CharacterConfig:
        """Create a custom character configuration."""
        personality = CharacterPersonality(
            name=name,
            description=description,
            **kwargs
        )
        
        config = CharacterConfig(
            character_type=CharacterType.CUSTOM,
            personality=personality,
            system_prompt=f"You are {name}. {description}",
            user_prefix="User: ",
            assistant_prefix=f"{name}: "
        )
        
        return config


# Global character manager instance
_character_manager: Optional[CharacterManager] = None


def get_character_manager() -> CharacterManager:
    """Get the global character manager instance."""
    global _character_manager
    
    if _character_manager is None:
        _character_manager = CharacterManager()
    
    return _character_manager


def get_character(character_name: str) -> Optional[CharacterConfig]:
    """Get a character configuration by name."""
    return get_character_manager().get_character(character_name)


def create_custom_character(name: str, description: str, **kwargs) -> CharacterConfig:
    """Create a custom character configuration."""
    return get_character_manager().create_custom_character(name, description, **kwargs)