from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime
import logging

# Import our custom modules
from config import Config
from services import OpenAIService, ElevenLabsService
from models import ChatRequest, ChatResponse, ChatMessageResponse, QuizQuestion
from utils import generate_user_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TechMeAnything API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
openai_service = OpenAIService()
elevenlabs_service = ElevenLabsService()

# Models are now imported from models package

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "TechMeAnything API is running!",
        "timestamp": datetime.now().isoformat()
    }

# Test endpoint to debug the issue
@app.post("/api/v1/chat/test")
async def test_endpoint():
    """Test endpoint to debug the issue"""
    try:
        return {"message": "Test endpoint working", "status": "success"}
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in test endpoint: {str(e)}")

# Main chat endpoint
@app.post("/api/v1/chat/message")
async def chat_message(
    chat_request: ChatRequest,
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Process user chat message and return AI response with optional audio/video/quiz"""
    try:
        logger.info(f"Processing chat message from user {x_user_id}: {chat_request.message.content}")
        
        # Check if this is a quiz request
        is_quiz_request = openai_service.should_generate_quiz(chat_request.message.content)
        logger.info(f"Is quiz request: {is_quiz_request}")
        
        # Generate AI response
        logger.info(f"Calling generate_chat_response with is_quiz_request={is_quiz_request}")
        ai_response = openai_service.generate_chat_response(
            user_message=chat_request.message.content,
            user_id=x_user_id,
            is_quiz_request=is_quiz_request
        )
        logger.info(f"AI response received: {ai_response[:100]}...")
        
        # Generate quiz if requested
        quiz_questions = []
        if is_quiz_request:
            logger.info("Generating quiz questions...")
            # Extract topic from the message for quiz generation
            topic = chat_request.message.content.lower()
            # Remove common quiz request words to get the topic
            for word in ["quiz", "test", "question", "assessment", "check my understanding", "test me", "questions"]:
                topic = topic.replace(word, "").strip()
            if not topic:
                topic = "general knowledge"
            
            quiz_questions = openai_service.generate_quiz(topic, "medium", 3)
            logger.info(f"Generated {len(quiz_questions)} quiz questions")
        
        # Generate response ID and timestamp
        response_id = str(uuid.uuid4())
        current_timestamp = datetime.now().isoformat()
        
        # Generate audio if requested
        audio_url = None
        if chat_request.requireAudio:
            logger.info("Generating audio...")
            audio_base64 = elevenlabs_service.generate_audio(ai_response)
            if audio_base64:
                audio_url = f"data:audio/mpeg;base64,{audio_base64}"
                logger.info("Audio generated successfully")
            else:
                logger.warning("Failed to generate audio, falling back to mock URL")
                audio_url = "https://example.com/mock-audio.mp3"
        
        # Build response
        response_data = {
            "success": True,
            "response": {
                "id": response_id,
                "messageId": chat_request.message.id,
                "content": ai_response,
                "timestamp": current_timestamp,
                "audioUrl": audio_url
            },
            "audioUrl": audio_url,
            "videoUrl": None,
            "quiz": quiz_questions if quiz_questions else []
        }
        
        logger.info(f"Successfully generated response for user {x_user_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

# ElevenLabs voices endpoint
@app.get("/api/v1/voices")
async def get_available_voices():
    """Get available ElevenLabs voices"""
    try:
        voices_data = elevenlabs_service.get_available_voices()
        if voices_data:
            return {
                "success": True,
                "voices": voices_data.get("voices", []),
                "count": len(voices_data.get("voices", []))
            }
        else:
            return {
                "success": False,
                "message": "Failed to fetch voices. Check ElevenLabs API key.",
                "voices": [],
                "count": 0
            }
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")

# Test audio generation endpoint
@app.post("/api/v1/audio/generate")
async def generate_test_audio(text: str, voice_id: str = None):
    """Generate audio from text for testing"""
    try:
        audio_base64 = elevenlabs_service.generate_audio(text, voice_id)
        if audio_base64:
            return {
                "success": True,
                "audio": f"data:audio/mpeg;base64,{audio_base64}",
                "message": "Audio generated successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to generate audio",
                "audio": None
            }
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
