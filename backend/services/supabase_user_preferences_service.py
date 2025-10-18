"""
Supabase User Preferences Service
Handles user preference storage and retrieval using Supabase
"""

import logging
from typing import Dict, Any, Optional
from supabase import create_client, Client
from config import Config

logger = logging.getLogger(__name__)

class SupabaseUserPreferencesService:
    def __init__(self):
        """Initialize Supabase client for user preferences"""
        self.supabase_url = Config.SUPABASE_URL
        self.supabase_key = Config.SUPABASE_KEY
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase URL or key not found in environment variables")
            self.supabase = None
            return
            
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase user preferences service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences from Supabase"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return self._get_default_preferences()
        
        try:
            response = self.supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                preferences = response.data[0]
                logger.info(f"Retrieved user preferences for user {user_id}")
                return {
                    "name": preferences.get("name", "Student"),
                    "grade_level": preferences.get("grade_level", "middle"),
                    "language": preferences.get("language", "en"),
                    "learning_style": preferences.get("learning_style", "reading"),
                    "preferred_subjects": preferences.get("preferred_subjects", [])
                }
            else:
                logger.info(f"No preferences found for user {user_id}, returning defaults")
                return self._get_default_preferences()
                
        except Exception as e:
            logger.error(f"Error retrieving user preferences for {user_id}: {e}")
            return self._get_default_preferences()

    def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Store user preferences in Supabase"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            # Prepare data for Supabase
            data = {
                "user_id": user_id,
                "name": preferences.get("name", "Student"),
                "grade_level": preferences.get("grade_level", "middle"),
                "language": preferences.get("language", "en"),
                "learning_style": preferences.get("learning_style", "reading"),
                "preferred_subjects": preferences.get("preferred_subjects", [])
            }
            
            # Use upsert to insert or update
            response = self.supabase.table("user_preferences").upsert(data).execute()
            
            if response.data:
                logger.info(f"Stored user preferences for user {user_id}")
                return True
            else:
                logger.error(f"Failed to store preferences for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing user preferences for {user_id}: {e}")
            return False

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update specific user preferences (uses upsert to handle new users)"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            # Only update non-empty values
            update_data = {k: v for k, v in preferences.items() if v is not None and v != ""}
            
            if not update_data:
                logger.warning(f"No valid data to update for user {user_id}")
                return False
            
            # Add user_id to the data for upsert
            update_data["user_id"] = user_id
            
            # Use proper upsert syntax for Supabase
            response = self.supabase.table("user_preferences").upsert(
                update_data,
                on_conflict="user_id"
            ).execute()
            
            if response.data:
                logger.info(f"Updated user preferences for user {user_id}")
                return True
            else:
                logger.error(f"Failed to update preferences for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating user preferences for {user_id}: {e}")
            return False

    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "name": "Student",
            "grade_level": "middle",
            "language": "en",
            "learning_style": "reading",
            "preferred_subjects": []
        }

    def should_generate_video(self, user_id: str, message: str) -> bool:
        """Determine if video should be generated based on user preferences and message content"""
        preferences = self.get_user_preferences(user_id)
        learning_style = preferences.get("learning_style", "reading")
        user_name = preferences.get("name", "Student")
        
        message_lower = message.lower().strip()
        
        # Skip video generation for simple greetings and non-educational content
        simple_greetings = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "how's it going", "nice to meet you",
            "thanks", "thank you", "bye", "goodbye", "see you later"
        ]
        
        if any(greeting in message_lower for greeting in simple_greetings):
            logger.info(f"No video generation for {user_name}: Simple greeting detected")
            return False
        
        # Check for explicit video keywords in message (always generate video)
        explicit_video_keywords = [
            "video", "show me", "demonstrate", "visual", "see", "watch", "animation",
            "create video", "generate video", "make a video", "visualize", "illustrate"
        ]
        
        for keyword in explicit_video_keywords:
            if keyword in message_lower:
                logger.info(f"Video generation triggered for {user_name}: Message contains video keyword '{keyword}'")
                return True
        
        # Check if user prefers video learning AND message contains educational content
        if learning_style == "video":
            # Look for educational content indicators
            educational_keywords = [
                "explain", "teach", "learn", "understand", "how does", "what is", "why",
                "atoms", "molecules", "chemistry", "physics", "biology", "math", "science",
                "history", "geography", "literature", "art", "music", "language",
                "concept", "theory", "process", "mechanism", "function", "structure"
            ]
            
            if any(keyword in message_lower for keyword in educational_keywords):
                logger.info(f"Video generation triggered for {user_name}: User prefers video learning and message contains educational content")
                return True
            else:
                logger.info(f"No video generation for {user_name}: User prefers video but message lacks educational content")
                return False
        
        logger.info(f"No video generation for {user_name}: Learning style is '{learning_style}' and no educational content detected")
        return False

    def should_generate_audio(self, user_id: str) -> bool:
        """Determine if audio should be generated based on user preferences"""
        preferences = self.get_user_preferences(user_id)
        learning_style = preferences.get("learning_style", "reading")
        
        return learning_style == "audio"

    def personalize_response(self, user_id: str, response: str) -> str:
        """Personalize response by adding user's name"""
        preferences = self.get_user_preferences(user_id)
        name = preferences.get("name", "Student")
        
        if name != "Student" and name not in response:
            return f"Hi {name}! {response}"
        return response
