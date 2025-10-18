"""
Mem0 Service for User Preferences and Session History
Handles user personalization and memory management using Mem0 Platform
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from config import Config

try:
    from mem0 import MemoryClient
except ImportError:
    MemoryClient = None

logger = logging.getLogger(__name__)

class Mem0Service:
    """Service class for Mem0 memory management"""
    
    def __init__(self):
        """Initialize Mem0 service"""
        self.mem0_api_key = Config.MEM0_API_KEY
        
        if not self.mem0_api_key:
            logger.warning("Mem0 API key not found. Mem0 features will be disabled.")
            self.client = None
            return
        
        if MemoryClient is None:
            logger.warning("Mem0 package not installed. Please install with: pip install mem0ai")
            self.client = None
            return
        
        try:
            os.environ["MEM0_API_KEY"] = self.mem0_api_key
            self.client = MemoryClient()
            logger.info("Mem0 service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0 service: {str(e)}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Mem0 service is available"""
        return self.client is not None
    
    def store_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store user preferences as long-term memories
        
        Args:
            user_id: Unique user identifier
            preferences: User preferences dictionary
            
        Returns:
            Result of the memory storage operation
        """
        if not self.is_available():
            return {"success": False, "error": "Mem0 service not available"}
        
        try:
            # Create messages for storing preferences
            messages = [
                {
                    "role": "user", 
                    "content": f"My preferences are: {self._format_preferences(preferences)}"
                },
                {
                    "role": "assistant", 
                    "content": f"I'll remember your preferences: {preferences.get('name', 'User')}."
                }
            ]
            
            result = self.client.add(
                messages, 
                user_id=user_id,
                metadata={
                    "category": "user_preferences",
                    "timestamp": datetime.now().isoformat(),
                    "preferences": preferences
                }
            )
            
            logger.info(f"Stored user preferences for user {user_id}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Error storing user preferences: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user preferences
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User preferences dictionary
        """
        if not self.is_available():
            return self._get_default_preferences()
        
        try:
            # Search for user preferences with proper filters
            results = self.client.search(
                "user preferences name grade language learning style",
                user_id=user_id,
                filters={"category": "user_preferences"}
            )
            
            if results and len(results) > 0:
                # Extract preferences from the most recent result
                latest_result = results[0]
                metadata = latest_result.get("metadata", {})
                preferences = metadata.get("preferences", {})
                
                if preferences:
                    logger.info(f"Retrieved user preferences for user {user_id}")
                    return preferences
            
            # Return default preferences if none found
            return self._get_default_preferences()
            
        except Exception as e:
            logger.error(f"Error retrieving user preferences: {str(e)}")
            return self._get_default_preferences()
    
    def store_session_history(
        self, 
        user_id: str, 
        session_id: str,
        user_message: str,
        ai_response: str,
        response_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Store session history for context
        
        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            user_message: User's message
            ai_response: AI's response
            response_type: Type of response (text, audio, video, quiz)
            
        Returns:
            Result of the memory storage operation
        """
        if not self.is_available():
            return {"success": False, "error": "Mem0 service not available"}
        
        try:
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ]
            
            result = self.client.add(
                messages,
                user_id=user_id,
                run_id=session_id,
                metadata={
                    "category": "session_history",
                    "response_type": response_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Stored session history for user {user_id}, session {session_id}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Error storing session history: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_session_history(
        self, 
        user_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent session history for context
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of recent sessions to retrieve
            
        Returns:
            List of recent session interactions
        """
        if not self.is_available():
            return []
        
        try:
            # Get all memories for the user with proper filters
            all_memories = self.client.get_all(
                user_id=user_id,
                filters={"category": "session_history"}
            )
            
            # Sort by timestamp (most recent first) and limit
            all_memories.sort(
                key=lambda x: x.get("metadata", {}).get("timestamp", ""), 
                reverse=True
            )
            
            return all_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving session history: {str(e)}")
            return []
    
    def get_learning_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning context for a user
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary containing user preferences and recent session history
        """
        preferences = self.get_user_preferences(user_id)
        session_history = self.get_session_history(user_id, limit=3)
        
        return {
            "preferences": preferences,
            "recent_sessions": session_history,
            "user_name": preferences.get("name", "Student"),
            "grade_level": preferences.get("grade", "middle"),
            "language": preferences.get("language", "en"),
            "learning_style": preferences.get("learning_style", "reading")
        }
    
    def should_generate_video(self, user_id: str, message: str) -> bool:
        """
        Determine if video should be generated based on user preferences and message
        
        Logic:
        1. If user's learning style is "video" → always generate video
        2. If message contains video keywords → generate video regardless of learning style
        
        Args:
            user_id: Unique user identifier
            message: User's message
            
        Returns:
            Boolean indicating if video should be generated
        """
        preferences = self.get_user_preferences(user_id)
        learning_style = preferences.get("learning_style", "reading")
        user_name = preferences.get("name", "Student")
        
        # Check if user prefers video learning
        if learning_style == "video":
            logger.info(f"Video generation triggered for {user_name}: User prefers video learning style")
            return True
        
        # Check if message explicitly requests video
        video_keywords = [
            "video", "show me", "demonstrate", "visual", "see how", 
            "watch", "animation", "explain with video", "create video",
            "generate video", "make a video", "visualize", "illustrate",
            "show", "display", "see", "look at"
        ]
        
        message_lower = message.lower()
        for keyword in video_keywords:
            if keyword in message_lower:
                logger.info(f"Video generation triggered for {user_name}: Message contains video keyword '{keyword}'")
                return True
        
        logger.info(f"No video generation for {user_name}: Learning style is '{learning_style}' and no video keywords found")
        return False
    
    def should_generate_audio(self, user_id: str) -> bool:
        """
        Determine if audio should be generated based on user preferences
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Boolean indicating if audio should be generated
        """
        preferences = self.get_user_preferences(user_id)
        learning_style = preferences.get("learning_style", "reading")
        
        return learning_style == "audio"
    
    def personalize_response(
        self, 
        user_id: str, 
        response: str
    ) -> str:
        """
        Personalize AI response with user's name and preferences
        
        Args:
            user_id: Unique user identifier
            response: Original AI response
            
        Returns:
            Personalized response
        """
        preferences = self.get_user_preferences(user_id)
        user_name = preferences.get("name", "Student")
        
        # Add personalized greeting if not already present
        if not any(greeting in response.lower() for greeting in [user_name.lower(), "hello", "hi"]):
            response = f"Hello {user_name}! {response}"
        
        return response
    
    def _format_preferences(self, preferences: Dict[str, Any]) -> str:
        """Format preferences for storage"""
        formatted = []
        for key, value in preferences.items():
            formatted.append(f"{key}: {value}")
        return ", ".join(formatted)
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "name": "Student",
            "grade": "middle",
            "language": "en",
            "learning_style": "reading",  # reading, audio, video
            "preferred_subjects": [],
            "difficulty_level": "medium"
        }
