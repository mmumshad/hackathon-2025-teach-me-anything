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
        """Update specific user preferences"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            # Only update non-empty values
            update_data = {k: v for k, v in preferences.items() if v is not None and v != ""}
            
            if not update_data:
                logger.warning(f"No valid data to update for user {user_id}")
                return False
            
            response = self.supabase.table("user_preferences").update(update_data).eq("user_id", user_id).execute()
            
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
        
        # Check if user prefers video learning
        if learning_style == "video":
            logger.info(f"Video generation triggered for {preferences.get('name', 'Student')}: User prefers video learning style")
            return True
        
        # Check for video keywords in message
        video_keywords = ["video", "show me", "demonstrate", "visual", "see", "watch", "animation"]
        message_lower = message.lower()
        
        for keyword in video_keywords:
            if keyword in message_lower:
                logger.info(f"Video generation triggered for {preferences.get('name', 'Student')}: Message contains video keyword '{keyword}'")
                return True
        
        logger.info(f"No video generation for {preferences.get('name', 'Student')}: Learning style is '{learning_style}' and no video keywords found")
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
