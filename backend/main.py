from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uuid
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
        # Return static mock response matching API contracts
        response = ChatResponse(
            id="resp-1",
            messageId=chat_request.message.id,
            content="Photosynthesis is the process where plants convert sunlight into energy. ",
            timestamp=datetime.now().isoformat()
        )
        
        if should_generate_quiz:
            logger.info("Generating quiz for user request")
            try:
                # Extract topic from the message for quiz generation
                topic = chat_request.message.content
                quiz_questions = await openai_service.generate_quiz(topic)
            except Exception as quiz_error:
                logger.warning(f"Failed to generate quiz: {str(quiz_error)}")
                # Continue without quiz if generation fails
        
        return ChatMessageResponse(
            success=True,
            response=response,
            audioUrl="http://localhost:3000/sample-video.mp3",  # Mock audio URL
            videoUrl="http://localhost:3000/sample-video.mp4",  # Your sample video
            quiz=quiz
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
