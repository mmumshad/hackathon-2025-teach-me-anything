"""
Intelligent Preference Extraction Service
Uses OpenAI LLM to intelligently extract user preferences from messages
"""

import logging
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class IntelligentPreferenceExtractionService:
    def __init__(self):
        """Initialize OpenAI client for preference extraction"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
            self.client = None
            return
            
        try:
            self.client = OpenAI(api_key=self.openai_api_key)
            logger.info("Intelligent preference extraction service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def extract_preferences_from_message(self, message: str, current_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract user preferences from a message using OpenAI LLM"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {}
        
        try:
            # Prepare the prompt for preference extraction
            system_prompt = """You are an intelligent assistant that extracts user preferences from educational chat messages. 
            Your task is to identify and extract the following information from user messages:
            
            1. **Name**: Extract the user's name if mentioned (first name only)
            2. **Grade Level**: Identify educational level (elementary, middle, high, college, adult)
            3. **Language**: Detect preferred language (en, es, fr, de, etc.)
            4. **Learning Style**: Identify preferred learning method (reading, audio, video, interactive)
            5. **Subjects**: Extract any mentioned subjects or topics of interest
            
            Return ONLY a JSON object with the extracted information. If no information is found for a field, omit it from the response.
            
            Example response:
            {
                "name": "Alice",
                "grade_level": "high",
                "language": "en",
                "learning_style": "video",
                "preferred_subjects": ["physics", "chemistry"]
            }
            
            Be conservative - only extract information that is clearly stated or strongly implied."""

            user_prompt = f"""Extract preferences from this message: "{message}"
            
            Current user preferences (for context): {current_preferences or "None"}
            
            Return only the JSON object with extracted preferences."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response for preference extraction: {content}")
            
            # Parse JSON response
            try:
                extracted_preferences = json.loads(content)
                logger.info(f"Successfully extracted preferences: {extracted_preferences}")
                return extracted_preferences
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting preferences from message: {e}")
            return {}

    def extract_name_from_message(self, message: str) -> Optional[str]:
        """Extract just the user's name from a message"""
        if not self.client:
            return None
        
        try:
            system_prompt = """You are a name extraction assistant. Extract the user's first name from their message.
            Return ONLY the first name, or null if no name is mentioned.
            
            Examples:
            - "My name is John" -> "John"
            - "I'm Sarah" -> "Sarah"
            - "Call me Alex" -> "Alex"
            - "Hello, I want to learn" -> null
            - "Hi there" -> null"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract name from: \"{message}\""}
                ],
                max_tokens=50,
                temperature=0.1
            )

            name = response.choices[0].message.content.strip()
            
            # Clean up the response
            if name.lower() in ['null', 'none', 'n/a', '']:
                return None
            
            # Remove quotes if present
            name = name.strip('"\'')
            
            logger.info(f"Extracted name: {name}")
            return name if name else None
            
        except Exception as e:
            logger.error(f"Error extracting name from message: {e}")
            return None

    def extract_learning_style_from_message(self, message: str) -> Optional[str]:
        """Extract learning style preference from a message"""
        if not self.client:
            return None
        
        try:
            system_prompt = """You are a learning style detection assistant. Analyze the message to determine the user's preferred learning style.
            
            Return ONE of these values:
            - "reading" (for text-based learning, books, articles)
            - "audio" (for listening, podcasts, audio content)
            - "video" (for visual learning, videos, demonstrations)
            - "interactive" (for hands-on, quizzes, interactive content)
            
            Return null if no clear preference is indicated."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze learning style preference: \"{message}\""}
                ],
                max_tokens=50,
                temperature=0.1
            )

            style = response.choices[0].message.content.strip().lower()
            
            valid_styles = ["reading", "audio", "video", "interactive"]
            if style in valid_styles:
                logger.info(f"Extracted learning style: {style}")
                return style
            
            logger.info("No clear learning style preference detected")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting learning style from message: {e}")
            return None

    def extract_grade_level_from_message(self, message: str) -> Optional[str]:
        """Extract grade level from a message"""
        if not self.client:
            return None
        
        try:
            system_prompt = """You are a grade level detection assistant. Analyze the message to determine the user's educational level.
            
            Return ONE of these values:
            - "elementary" (K-5, ages 5-10)
            - "middle" (6-8, ages 11-13)
            - "high" (9-12, ages 14-18)
            - "college" (undergraduate level)
            - "adult" (post-college, professional)
            
            Return null if no clear grade level is indicated."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze grade level: \"{message}\""}
                ],
                max_tokens=50,
                temperature=0.1
            )

            grade = response.choices[0].message.content.strip().lower()
            
            valid_grades = ["elementary", "middle", "high", "college", "adult"]
            if grade in valid_grades:
                logger.info(f"Extracted grade level: {grade}")
                return grade
            
            logger.info("No clear grade level detected")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting grade level from message: {e}")
            return None

    def extract_subjects_from_message(self, message: str) -> List[str]:
        """Extract mentioned subjects or topics from a message"""
        if not self.client:
            return []
        
        try:
            system_prompt = """You are a subject extraction assistant. Extract educational subjects or topics mentioned in the message.
            
            Return a JSON array of subjects. Use common subject names like:
            - "mathematics", "physics", "chemistry", "biology"
            - "history", "geography", "literature", "english"
            - "computer science", "programming", "art", "music"
            
            Return an empty array if no subjects are mentioned."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract subjects from: \"{message}\""}
                ],
                max_tokens=100,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            
            try:
                subjects = json.loads(content)
                if isinstance(subjects, list):
                    logger.info(f"Extracted subjects: {subjects}")
                    return subjects
                else:
                    return []
            except json.JSONDecodeError:
                logger.info("No subjects extracted")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting subjects from message: {e}")
            return []

    def merge_preferences(self, existing_preferences: Dict[str, Any], new_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new preferences with existing ones"""
        merged = existing_preferences.copy()
        
        for key, value in new_preferences.items():
            if value is not None and value != "":
                if key == "preferred_subjects" and isinstance(value, list):
                    # Merge subject lists
                    existing_subjects = merged.get("preferred_subjects", [])
                    merged[key] = list(set(existing_subjects + value))
                else:
                    merged[key] = value
        
        logger.info(f"Merged preferences: {merged}")
        return merged
