"""
Intent Recognition Service
Uses OpenAI LLM to intelligently detect user intent from messages
"""

import logging
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
import os
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    QUIZ = "quiz"
    VIDEO = "video"
    AUDIO = "audio"
    AUDIOBOOK = "audiobook"
    CONTENT = "content"
    MATERIAL_REQUEST = "material_request"
    GREETING = "greeting"
    UNKNOWN = "unknown"

class IntentRecognitionService:
    def __init__(self):
        """Initialize OpenAI client for intent recognition"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
            self.client = None
            return
            
        try:
            self.client = OpenAI(api_key=self.openai_api_key)
            logger.info("Intent recognition service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def detect_intent(self, message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect user intent from a message using OpenAI LLM
        
        Args:
            message: User's message
            user_context: User preferences and context (learning style, name, etc.)
            
        Returns:
            Dictionary with intent detection results
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return self._fallback_intent_detection(message)
        
        try:
            # Prepare the prompt for intent detection
            system_prompt = """You are an intelligent educational assistant that analyzes user messages to detect their intent.

Your task is to classify the user's message into one of these intent categories:

1. **QUIZ** - User wants to be tested/quizzed on a topic
   - Keywords: "quiz", "test", "question", "assessment", "check my understanding", "test me"
   - Examples: "Quiz me on atoms", "Test my knowledge", "Give me questions about physics"

2. **VIDEO** - User wants visual content or video explanation
   - Keywords: "video", "show me", "demonstrate", "visual", "see", "watch", "animation"
   - Examples: "Show me a video of atoms", "Demonstrate how photosynthesis works", "Create a video"

3. **AUDIO** - User wants audio explanation or voice response
   - Keywords: "audio", "speak", "tell me", "voice", "hear", "listen"
   - Examples: "Give me audio explanation", "Speak the answer", "Tell me about atoms"

4. **AUDIOBOOK** - User wants to convert content to audiobook format
   - Keywords: "audiobook", "read to me", "convert to audio", "narrate"
   - Examples: "Convert this to audiobook", "Read this document to me"

5. **MATERIAL_REQUEST** - User wants recommendations for study materials
   - Keywords: "recommend", "suggest", "book", "resource", "study material", "course"
   - Examples: "Recommend books on physics", "Suggest study materials", "What should I read?"

6. **CONTENT** - User wants educational content/explanation (default for learning)
   - Keywords: "explain", "teach", "learn", "understand", "what is", "how does", "why"
   - Examples: "Explain atoms", "Teach me physics", "What is photosynthesis?"

7. **GREETING** - Simple greetings and non-educational conversation
   - Keywords: "hello", "hi", "hey", "how are you", "thanks", "bye"
   - Examples: "Hello", "Hi there", "How are you?"

8. **UNKNOWN** - Intent cannot be determined

Return ONLY a JSON object with this structure:
{
    "intent": "quiz|video|audio|audiobook|content|material_request|greeting|unknown",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this intent was chosen",
    "keywords_found": ["keyword1", "keyword2"],
    "suggested_response_type": "quiz|video|audio|content|text"
}

Be precise and conservative. If unsure, choose the most likely intent based on context."""

            user_prompt = f"""Analyze this user message for intent: "{message}"

User Context: {user_context or "No context available"}

Return only the JSON object with intent analysis."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using faster, cheaper model for intent detection
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=300
            )

            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Remove any markdown formatting
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                elif response_text.startswith("```"):
                    response_text = response_text.replace("```", "").strip()
                
                intent_result = json.loads(response_text)
                
                # Validate the response structure
                required_fields = ["intent", "confidence", "reasoning"]
                if all(field in intent_result for field in required_fields):
                    logger.info(f"Intent detected: {intent_result['intent']} (confidence: {intent_result['confidence']})")
                    return intent_result
                else:
                    logger.warning(f"Invalid intent response structure: {intent_result}")
                    return self._fallback_intent_detection(message)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse intent response as JSON: {e}")
                logger.error(f"Raw response: {response_text}")
                return self._fallback_intent_detection(message)

        except Exception as e:
            logger.error(f"Error in intent detection: {e}")
            return self._fallback_intent_detection(message)

    def _fallback_intent_detection(self, message: str) -> Dict[str, Any]:
        """Fallback keyword-based intent detection when OpenAI is unavailable"""
        logger.info("Using fallback keyword-based intent detection")
        
        message_lower = message.lower().strip()
        
        # Simple keyword matching as fallback
        quiz_keywords = ["quiz", "test", "question", "assessment", "check my understanding", "test me"]
        video_keywords = ["video", "show me", "demonstrate", "visual", "see", "watch", "animation"]
        audio_keywords = ["audio", "speak", "tell me", "voice", "hear", "listen"]
        audiobook_keywords = ["audiobook", "read to me", "convert to audio", "narrate"]
        material_keywords = ["recommend", "suggest", "book", "resource", "study material", "course"]
        greeting_keywords = ["hello", "hi", "hey", "how are you", "thanks", "bye", "good morning", "good afternoon"]
        
        if any(keyword in message_lower for keyword in quiz_keywords):
            return {
                "intent": "quiz",
                "confidence": 0.8,
                "reasoning": "Keyword-based detection: quiz keywords found",
                "keywords_found": [kw for kw in quiz_keywords if kw in message_lower],
                "suggested_response_type": "quiz"
            }
        elif any(keyword in message_lower for keyword in video_keywords):
            return {
                "intent": "video",
                "confidence": 0.8,
                "reasoning": "Keyword-based detection: video keywords found",
                "keywords_found": [kw for kw in video_keywords if kw in message_lower],
                "suggested_response_type": "video"
            }
        elif any(keyword in message_lower for keyword in audio_keywords):
            return {
                "intent": "audio",
                "confidence": 0.8,
                "reasoning": "Keyword-based detection: audio keywords found",
                "keywords_found": [kw for kw in audio_keywords if kw in message_lower],
                "suggested_response_type": "audio"
            }
        elif any(keyword in message_lower for keyword in audiobook_keywords):
            return {
                "intent": "audiobook",
                "confidence": 0.8,
                "reasoning": "Keyword-based detection: audiobook keywords found",
                "keywords_found": [kw for kw in audiobook_keywords if kw in message_lower],
                "suggested_response_type": "audio"
            }
        elif any(keyword in message_lower for keyword in material_keywords):
            return {
                "intent": "material_request",
                "confidence": 0.8,
                "reasoning": "Keyword-based detection: material request keywords found",
                "keywords_found": [kw for kw in material_keywords if kw in message_lower],
                "suggested_response_type": "content"
            }
        elif any(keyword in message_lower for keyword in greeting_keywords):
            return {
                "intent": "greeting",
                "confidence": 0.9,
                "reasoning": "Keyword-based detection: greeting keywords found",
                "keywords_found": [kw for kw in greeting_keywords if kw in message_lower],
                "suggested_response_type": "text"
            }
        else:
            return {
                "intent": "content",
                "confidence": 0.6,
                "reasoning": "Fallback: assuming educational content request",
                "keywords_found": [],
                "suggested_response_type": "content"
            }

    def should_generate_quiz(self, message: str, user_context: Dict[str, Any] = None) -> bool:
        """Determine if quiz should be generated based on intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result["intent"] == "quiz"

    def should_generate_video(self, message: str, user_context: Dict[str, Any] = None) -> bool:
        """Determine if video should be generated based on intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result["intent"] == "video"

    def should_generate_audio(self, message: str, user_context: Dict[str, Any] = None) -> bool:
        """Determine if audio should be generated based on intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result["intent"] in ["audio", "audiobook"]

    def should_generate_audiobook(self, message: str, user_context: Dict[str, Any] = None) -> bool:
        """Determine if audiobook should be generated based on intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result["intent"] == "audiobook"

    def is_material_request(self, message: str, user_context: Dict[str, Any] = None) -> bool:
        """Determine if this is a material request based on intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result["intent"] == "material_request"

    def is_greeting(self, message: str, user_context: Dict[str, Any] = None) -> bool:
        """Determine if this is a greeting based on intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result["intent"] == "greeting"

    def get_intent_confidence(self, message: str, user_context: Dict[str, Any] = None) -> float:
        """Get confidence score for intent detection"""
        intent_result = self.detect_intent(message, user_context)
        return intent_result.get("confidence", 0.0)
