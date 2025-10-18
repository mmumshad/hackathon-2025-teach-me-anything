from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
from typing import Optional, List

# Load environment variables
load_dotenv("../backend.env")

app = FastAPI(title="TechMeAnything API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models matching API contracts
class ChatMessage(BaseModel):
    id: str
    userId: str
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    message: ChatMessage
    requireAudio: Optional[bool] = False

class QuizOption(BaseModel):
    id: str
    text: str

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[QuizOption]
    correctAnswerId: str
    explanation: str

class ChatResponse(BaseModel):
    id: str
    messageId: str
    content: str
    timestamp: str
    audioUrl: Optional[str] = None

class ChatMessageResponse(BaseModel):
    success: bool
    response: ChatResponse
    audioUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    quiz: Optional[List[QuizQuestion]] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "TechMeAnything API is running!",
        "timestamp": datetime.now().isoformat()
    }

# Main chat endpoint
@app.post("/api/v1/chat/message")
async def chat_message(
    chat_request: ChatRequest,
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Process user chat message and return AI response with optional audio/video/quiz"""
    try:
        # Return static mock response
        return {
            "responses": [
                {
                    "id": "resp-1",
                    "messageId": "msg-1", 
                    "content": "Photosynthesis is the process where plants convert sunlight into energy...",
                    "timestamp": "2024-01-01T00:00:01Z",
                    "audioUrl": "https://mock-audio.com/photosynthesis.mp3",
                    "videoUrl": "https://mock-video.com/photosynthesis.mp4",
                    "quiz": [
                        {
                            "id": "q1",
                            "question": "What gas do plants absorb?",
                            "options": [
                                {"id": "a", "text": "Oxygen"},
                                {"id": "b", "text": "Carbon Dioxide"}
                            ],
                            "correctAnswerId": "b",
                            "explanation": "Plants absorb carbon dioxide from the atmosphere."
                        }
                    ]
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
