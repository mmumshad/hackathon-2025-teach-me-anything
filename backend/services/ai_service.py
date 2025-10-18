"""
OpenAI service module for TechMeAnything API
Handles chat completions and quiz generation
"""

import openai
from typing import List, Dict, Optional, Any
import json
import re
import logging
from config import Config

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service class for OpenAI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI client with API key"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required but not found in configuration")
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def generate_chat_response(
        self,
        user_message: str,
        user_id: str,
        grade_level: Optional[str] = None,
        is_quiz_request: bool = False,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a chat response using OpenAI
        
        Args:
            user_message: The user's message
            user_id: Unique identifier for the user
            grade_level: Optional grade level for personalized responses
            is_quiz_request: Whether this is a quiz request
            chat_history: Optional list of previous chat messages for context
            
        Returns:
            Generated response text
        """
        try:
            # Build system prompt for educational context
            system_prompt = self._build_system_prompt(grade_level, is_quiz_request)
            
            # Build messages list with chat history context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history)
                logger.info(f"Added {len(chat_history)} previous messages to context")
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=80 if not is_quiz_request else Config.MAX_RESPONSE_LENGTH,
                temperature=0.7
            )
            
            ai_content = response.choices[0].message.content.strip()
            
            # Post-process quiz requests to ensure clean response
            if is_quiz_request:
                ai_content = self._clean_quiz_response(ai_content)
            
            return ai_content
            
        except Exception as e:
            raise Exception(f"Error generating chat response: {str(e)}")
    
    def generate_quiz(
        self, 
        topic: str, 
        difficulty_level: str = "medium",
        num_questions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a given topic
        
        Args:
            topic: The topic to generate quiz questions for
            difficulty_level: Easy, medium, or hard
            num_questions: Number of questions to generate
            
        Returns:
            List of quiz questions with options and answers
        """
        try:
            prompt = self._build_quiz_prompt(topic, difficulty_level, num_questions)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert quiz generator for educational content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            quiz_text = response.choices[0].message.content.strip()
            return self._parse_quiz_response(quiz_text, num_questions)
            
        except Exception as e:
            raise Exception(f"Error generating quiz: {str(e)}")
    
    def _build_system_prompt(self, grade_level: Optional[str] = None, is_quiz_request: bool = False) -> str:
        """Build system prompt for educational AI assistant"""
        if is_quiz_request:
            base_prompt = """You are an intelligent educational AI assistant for K12 students. 
            
            CRITICAL INSTRUCTION: The user is requesting a quiz/test. 
            
            Your response must be EXACTLY ONE SENTENCE that:
            - Acknowledges you'll help test their knowledge
            - Is encouraging and supportive
            - Does NOT include any quiz questions, numbered lists, or question formats
            
            Examples of CORRECT responses:
            - "Great! I'd love to help you test your knowledge!"
            - "Perfect! Let's see how much you know about this topic!"
            - "Excellent! I'll prepare some questions for you."
            
            FORBIDDEN: Do NOT include quiz questions, numbered lists, or "Here is a quiz" phrases."""
        else:
            base_prompt = """You are an intelligent educational AI assistant for K12 students. 
            Your role is to:
            1. Provide clear, engaging, and age-appropriate explanations
            2. Use simple language that students can understand
            3. Include examples and analogies when helpful
            4. Encourage curiosity and learning
            5. Be supportive and encouraging
            6. If asked about quizzes or assessments, mention that you can create educational quizzes
            7. If asked about videos or visual content, mention that you can generate educational videos
            
            IMPORTANT VIDEO RESPONSE RULE: When users ask for videos or visual content, your response must be EXACTLY: "Creating a video for you now...." Do not customize this message or add any other text.
            
            CRITICAL: Keep your response to 50 words or less. Be concise and focused on the key points.
            
            Always be positive, patient, and educational in your responses."""
        
        if grade_level:
            base_prompt += f"\n\nThe student is in grade {grade_level}. Adjust your language and examples accordingly."
        
        return base_prompt
    
    def _build_quiz_prompt(self, topic: str, difficulty_level: str, num_questions: int) -> str:
        """Build prompt for quiz generation"""
        return f"""Create {num_questions} multiple choice quiz questions about "{topic}" at {difficulty_level} difficulty level.

For each question, provide:
1. A clear question
2. 4 answer options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format your response as JSON with this structure:
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": [
                {{"id": "a", "text": "Option A"}},
                {{"id": "b", "text": "Option B"}},
                {{"id": "c", "text": "Option C"}},
                {{"id": "d", "text": "Option D"}}
            ],
            "correct_answer_id": "b",
            "explanation": "Explanation of why this is correct"
        }}
    ]
}}

Make sure the questions are educational and test understanding of the topic."""
    
    def _parse_quiz_response(self, quiz_text: str, num_questions: int) -> List[Dict[str, Any]]:
        """Parse OpenAI response into structured quiz format"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', quiz_text, re.DOTALL)
            if json_match:
                quiz_data = json.loads(json_match.group())
                questions = quiz_data.get('questions', [])
                
                # Convert to our API format
                formatted_questions = []
                for i, q in enumerate(questions[:num_questions]):
                    formatted_questions.append({
                        "id": f"q{i+1}",
                        "question": q.get("question", ""),
                        "options": q.get("options", []),
                        "correctAnswerId": q.get("correct_answer_id", ""),
                        "explanation": q.get("explanation", "")
                    })
                
                return formatted_questions
            else:
                # Fallback: create a simple quiz if JSON parsing fails
                return self._create_fallback_quiz(quiz_text)
                
        except (json.JSONDecodeError, Exception) as e:
            # Fallback to a simple quiz structure
            return self._create_fallback_quiz(quiz_text)
    
    def _create_fallback_quiz(self, quiz_text: str) -> List[Dict[str, Any]]:
        """Create a fallback quiz if parsing fails"""
        return [{
            "id": "q1",
            "question": "What did you learn from this topic?",
            "options": [
                {"id": "a", "text": "Basic concepts"},
                {"id": "b", "text": "Advanced concepts"},
                {"id": "c", "text": "I'm not sure"},
                {"id": "d", "text": "All of the above"}
            ],
            "correctAnswerId": "a",
            "explanation": "Learning basic concepts is the foundation of understanding any topic."
        }]
    
    def _clean_quiz_response(self, response: str) -> str:
        """Clean quiz response to ensure it only contains acknowledgment"""
        # Always replace quiz responses with simple acknowledgment
        # Since this function is only called for quiz requests, we should always clean
        acknowledgments = [
            "Great! I'd love to help you test your knowledge!",
            "Perfect! Let's see how much you know about this topic!",
            "Excellent! I'll prepare some questions for you.",
            "Awesome! Let's test what you've learned!",
            "Wonderful! I'll create some questions to help you practice!"
        ]
        import random
        return random.choice(acknowledgments)
    
    def should_generate_quiz(self, message: str) -> bool:
        """Determine if the message requests a quiz"""
        quiz_keywords = [
            "quiz", "test", "question", "assessment", 
            "check my understanding", "test me", "questions"
        ]
        return any(keyword in message.lower() for keyword in quiz_keywords)
    
    def should_generate_video(self, message: str) -> bool:
        """Determine if the message requests video generation"""
        video_keywords = [
            "video", "show me", "demonstrate", "visual", "see how", 
            "watch", "animation", "explain with video", "create video",
            "generate video", "make a video", "visualize", "illustrate"
        ]
        return any(keyword in message.lower() for keyword in video_keywords)
    
    def extract_video_prompt(self, message: str, ai_response: str) -> str:
        """Extract or create a video prompt from the user message and AI response"""
        # If user explicitly asks for video, use their request
        if any(keyword in message.lower() for keyword in ["video", "show me", "demonstrate", "visualize"]):
            # Extract the main topic from the message
            topic = message.lower()
            # Remove common video request words
            for word in ["video", "show me", "demonstrate", "visualize", "create", "generate", "make", "please", "can you"]:
                topic = topic.replace(word, "").strip()
            
            if topic:
                return f"Educational video showing: {topic.strip()}"
        
        # Otherwise, create a video prompt based on the AI response content
        # Take the first sentence or key concept from the response
        sentences = ai_response.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 50:
                first_sentence = first_sentence[:50] + "..."
            return f"Educational video explaining: {first_sentence}"
        
        return "Educational video explaining the concept"