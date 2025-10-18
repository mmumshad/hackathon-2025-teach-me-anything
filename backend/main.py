from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uuid
import random
from datetime import datetime
import logging

# Import our custom modules
from config import Config
from services import OpenAIService
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

# Initialize OpenAI service
openai_service = OpenAIService()

# Models are now imported from models package

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "TechMeAnything API is running!",
        "timestamp": datetime.now().isoformat()
    }

# Main chat endpoint
@app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
async def chat_message(
    chat_request: ChatRequest,
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Process user chat message and return AI response with optional audio/video/quiz"""
    try:
        # Randomly select response type
        response_type = random.choice(["text_only", "video_audio", "quiz"])
        
        # Base response
        response = ChatResponse(
            id=f"resp-{uuid.uuid4().hex[:8]}",
            messageId=chat_request.message.id,
            content="",
            timestamp=datetime.now().isoformat()
        )
        
        # Initialize optional fields
        audio_url = None
        video_url = None
        quiz = None
        
        if response_type == "text_only":
            response.content = "The water cycle is a continuous process where water evaporates from oceans, forms clouds, and returns to Earth as precipitation. This natural process helps distribute water across the planet and supports all life forms."
            
        elif response_type == "video_audio":
            response.content = "Photosynthesis is the amazing process where plants convert sunlight into energy! They absorb carbon dioxide from the air and water from the soil, then use sunlight to create glucose and release oxygen that we breathe."
            audio_url = "http://localhost:3000/sample-video.mp3"
            video_url = "http://localhost:3000/sample-video.mp4"
            
        elif response_type == "quiz":
            response.content = "Let's test your knowledge about the solar system! The sun is at the center, and planets orbit around it in elliptical paths."
            quiz = [
                QuizQuestion(
                    id="q1",
                    question="Which planet is closest to the Sun?",
                    options=[
                        QuizOption(id="a", text="Venus"),
                        QuizOption(id="b", text="Mercury"),
                        QuizOption(id="c", text="Earth"),
                        QuizOption(id="d", text="Mars")
                    ],
                    correctAnswerId="b",
                    explanation="Mercury is the closest planet to the Sun, completing an orbit in just 88 Earth days!"
                ),
                QuizQuestion(
                    id="q2",
                    question="What is the largest planet in our solar system?",
                    options=[
                        QuizOption(id="a", text="Saturn"),
                        QuizOption(id="b", text="Jupiter"),
                        QuizOption(id="c", text="Neptune"),
                        QuizOption(id="d", text="Uranus")
                    ],
                    correctAnswerId="b",
                    explanation="Jupiter is the largest planet in our solar system, with a mass greater than all other planets combined!"
                )
            ]
        
        return ChatMessageResponse(
            success=True,
            response=response,
            audioUrl=audio_url,
            videoUrl=video_url,
            quiz=quiz
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
