"""
User Onboarding Service
Handles friendly preference collection for new users
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class OnboardingStep(Enum):
    """Enum for onboarding steps"""
    WELCOME = "welcome"
    NAME = "name"
    LANGUAGE = "language"
    LEARNING_STYLE = "learning_style"
    COMPLETE = "complete"

class UserOnboardingService:
    """Service for handling user onboarding and preference collection"""
    
    def __init__(self):
        """Initialize the onboarding service"""
        self.onboarding_steps = [
            OnboardingStep.NAME,
            OnboardingStep.LANGUAGE,
            OnboardingStep.LEARNING_STYLE
        ]
    
    def should_start_onboarding(self, user_preferences: Dict[str, Any]) -> bool:
        """
        Check if user needs onboarding based on their preferences
        
        Args:
            user_preferences: Current user preferences
            
        Returns:
            True if user needs onboarding, False otherwise
        """
        # Check if user has default preferences (indicating no real preferences set)
        default_prefs = self._get_default_preferences()
        
        # If user has default name "Student", they need onboarding
        if user_preferences.get("name") == default_prefs.get("name"):
            return True
            
        # Check if essential preferences are missing or have default values
        # Only check for truly default/empty values, not just matching defaults
        
        # Name must not be "Student" (already checked above)
        name = user_preferences.get("name")
        if not name or name == "Student":
            return True
            
        # Language must be present (but can be any valid language)
        language = user_preferences.get("language")
        if not language:
            return True
            
        # Learning style must be present and not default
        learning_style = user_preferences.get("learning_style")
        if not learning_style or learning_style == default_prefs.get("learning_style"):
            return True
                
        return False
    
    def get_onboarding_response(
        self, 
        user_message: str, 
        user_preferences: Dict[str, Any],
        collected_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate onboarding response based on current step
        
        Args:
            user_message: User's current message
            user_preferences: Current user preferences
            collected_preferences: Preferences collected so far in this session
            
        Returns:
            Dictionary with onboarding response and next step
        """
        if collected_preferences is None:
            collected_preferences = {}
        
        # Determine current step
        current_step = self._get_current_step(collected_preferences)
        
        # Extract preference from user message if possible
        extracted_preference = self._extract_preference_from_message(user_message, current_step)
        
        if extracted_preference:
            collected_preferences.update(extracted_preference)
            current_step = self._get_current_step(collected_preferences)
        
        # Generate response for current step
        response_data = self._generate_step_response(current_step, collected_preferences, user_message)
        
        return {
            "is_onboarding": True,
            "current_step": current_step.value,
            "collected_preferences": collected_preferences,
            "response": response_data["response"],
            "is_complete": current_step == OnboardingStep.COMPLETE,
            "next_step": response_data.get("next_step")
        }
    
    def _get_current_step(self, collected_preferences: Dict[str, Any]) -> OnboardingStep:
        """Determine current onboarding step based on collected preferences"""
        if not collected_preferences.get("name"):
            return OnboardingStep.NAME
        elif not collected_preferences.get("language"):
            return OnboardingStep.LANGUAGE
        elif not collected_preferences.get("learning_style"):
            return OnboardingStep.LEARNING_STYLE
        else:
            return OnboardingStep.COMPLETE
    
    def _extract_preference_from_message(
        self, 
        message: str, 
        current_step: OnboardingStep
    ) -> Optional[Dict[str, Any]]:
        """Extract preference from user message based on current step"""
        message_lower = message.lower().strip()
        
        if current_step == OnboardingStep.NAME:
            # Extract name from message - look for "my name is" or "I'm" patterns
            if "my name is" in message_lower:
                # Extract name after "my name is"
                parts = message_lower.split("my name is")
                if len(parts) > 1:
                    name_part = parts[1].strip()
                    # Take the first word as the name
                    name = name_part.split()[0] if name_part.split() else None
                    if name and len(name) > 1:
                        return {"name": name.title()}
            
            elif "i'm" in message_lower or "i am" in message_lower:
                # Extract name after "I'm" or "I am"
                for pattern in ["i'm", "i am"]:
                    if pattern in message_lower:
                        parts = message_lower.split(pattern)
                        if len(parts) > 1:
                            name_part = parts[1].strip()
                            name = name_part.split()[0] if name_part.split() else None
                            if name and len(name) > 1:
                                return {"name": name.title()}
            
            # Fallback: extract first meaningful word (but be more selective)
            words = message.split()
            for word in words:
                # Skip common words and greetings
                if word.lower() not in ["hi", "hello", "hey", "my", "name", "is", "i'm", "i", "am", "want", "to", "learn", "about", "chemistry", "physics", "math", "science", "!", "?", ".", ","]:
                    # Clean the word (remove punctuation)
                    clean_name = ''.join(c for c in word if c.isalnum())
                    if len(clean_name) > 1 and clean_name.lower() not in ["hi", "hello", "hey"]:  # Must be at least 2 characters and not a greeting
                        return {"name": clean_name.title()}
        
        elif current_step == OnboardingStep.LANGUAGE:
            # Extract language preference
            language_mapping = {
                "english": "en",
                "spanish": "es", 
                "french": "fr",
                "german": "de",
                "italian": "it",
                "portuguese": "pt",
                "chinese": "zh",
                "japanese": "ja",
                "korean": "ko",
                "arabic": "ar",
                "hindi": "hi",
                "russian": "ru"
            }
            
            for lang_name, lang_code in language_mapping.items():
                if lang_name in message_lower:
                    return {"language": lang_code}
            
            # Default to English if user says yes, please, etc.
            if any(word in message_lower for word in ["yes", "sure", "ok", "okay", "fine", "please", "english"]):
                return {"language": "en"}
        
        elif current_step == OnboardingStep.LEARNING_STYLE:
            # Extract learning style preference
            if any(word in message_lower for word in ["reading", "read", "text", "books"]):
                return {"learning_style": "reading"}
            elif any(word in message_lower for word in ["audio", "listen", "sound", "hearing"]):
                return {"learning_style": "audio"}
            elif any(word in message_lower for word in ["video", "watch", "visual", "see", "visual"]):
                return {"learning_style": "video"}
            elif any(word in message_lower for word in ["1", "one", "first"]):
                return {"learning_style": "reading"}
            elif any(word in message_lower for word in ["2", "two", "second"]):
                return {"learning_style": "audio"}
            elif any(word in message_lower for word in ["3", "three", "third"]):
                return {"learning_style": "video"}
        
        return None
    
    def _generate_step_response(
        self, 
        current_step: OnboardingStep, 
        collected_preferences: Dict[str, Any],
        user_message: str
    ) -> Dict[str, Any]:
        """Generate response for current onboarding step"""
        
        if current_step == OnboardingStep.NAME:
            return {
                "response": "Hi there! 👋 I'm your AI learning assistant. I'd love to get to know you better so I can personalize your learning experience. What's your name? (Just tell me your first name, like 'My name is John' or 'I'm Sarah')",
                "next_step": OnboardingStep.LANGUAGE.value
            }
        
        elif current_step == OnboardingStep.LANGUAGE:
            name = collected_preferences.get("name", "there")
            return {
                "response": f"Nice to meet you, {name}! 😊 What language would you prefer for our conversations? You can say 'English', 'Spanish', 'French', or any other language you're comfortable with.",
                "next_step": OnboardingStep.LEARNING_STYLE.value
            }
        
        elif current_step == OnboardingStep.LEARNING_STYLE:
            name = collected_preferences.get("name", "there")
            language = collected_preferences.get("language", "en")
            lang_name = self._get_language_name(language)
            
            return {
                "response": f"Great, {name}! I'll communicate with you in {lang_name}. 🎯 Now, how do you prefer to learn? I can help you in different ways:\n\n1. 📖 **Reading** - I'll provide detailed written explanations\n2. 🎧 **Audio** - I'll generate audio explanations for you to listen to\n3. 🎥 **Video** - I'll create visual videos to explain concepts\n\nJust tell me your preference (1, 2, or 3, or describe it in your own words)!",
                "next_step": OnboardingStep.COMPLETE.value
            }
        
        elif current_step == OnboardingStep.COMPLETE:
            name = collected_preferences.get("name", "there")
            language = collected_preferences.get("language", "en")
            learning_style = collected_preferences.get("learning_style", "reading")
            
            lang_name = self._get_language_name(language)
            style_name = self._get_learning_style_name(learning_style)
            
            return {
                "response": f"Perfect, {name}! 🎉 I've got everything I need to help you learn effectively:\n\n✅ **Name**: {name}\n✅ **Language**: {lang_name}\n✅ **Learning Style**: {style_name}\n\nNow I'm ready to help you with your learning journey! What would you like to learn about today?",
                "next_step": None
            }
        
        return {
            "response": "Let's get started with setting up your preferences!",
            "next_step": OnboardingStep.NAME.value
        }
    
    def _get_language_name(self, language_code: str) -> str:
        """Get language name from language code"""
        language_names = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "hi": "Hindi",
            "ru": "Russian"
        }
        return language_names.get(language_code, "English")
    
    def _get_learning_style_name(self, learning_style: str) -> str:
        """Get learning style name"""
        style_names = {
            "reading": "Reading",
            "audio": "Audio",
            "video": "Video"
        }
        return style_names.get(learning_style, "Reading")
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "name": "Student",
            "grade": "middle",
            "language": "en",
            "learning_style": "reading",
            "preferred_subjects": [],
            "difficulty_level": "medium"
        }
    
    def merge_preferences(
        self, 
        existing_preferences: Dict[str, Any], 
        collected_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge collected preferences with existing ones
        
        Args:
            existing_preferences: Current user preferences
            collected_preferences: Newly collected preferences
            
        Returns:
            Merged preferences dictionary
        """
        merged = existing_preferences.copy()
        merged.update(collected_preferences)
        
        # Set defaults for any missing fields
        defaults = self._get_default_preferences()
        for key, value in defaults.items():
            if key not in merged:
                merged[key] = value
        
        return merged
