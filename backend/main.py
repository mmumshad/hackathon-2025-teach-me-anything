from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
from datetime import datetime
import logging
import os

# Import our custom modules
from config import Config
from services import OpenAIService
from services.openai_video_service import OpenAIVideoService
from services import OpenAIService, ElevenLabsService
from services.mem0_service import Mem0Service
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
video_service = OpenAIVideoService()
elevenlabs_service = ElevenLabsService()
mem0_service = Mem0Service()

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
@app.post("/api/v1/chat/message")
async def chat_message(
    chat_request: ChatRequest,
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Process user chat message and return AI response with optional audio/video/quiz"""
    try:
        logger.info(f"Processing chat message from user {x_user_id}: {chat_request.message.content}")
        
        # Get user learning context from Mem0
        learning_context = mem0_service.get_learning_context(x_user_id)
        user_preferences = learning_context["preferences"]
        user_name = learning_context["user_name"]
        grade_level = learning_context["grade_level"]
        language = learning_context["language"]
        learning_style = learning_context["learning_style"]
        
        logger.info(f"User context - Name: {user_name}, Grade: {grade_level}, Language: {language}, Learning Style: {learning_style}")
        
        # Check if user requested a quiz
        should_generate_quiz = openai_service.should_generate_quiz(chat_request.message.content)
        logger.info(f"Is quiz request: {should_generate_quiz}")
        
        # Check if video should be generated based on user preferences and message
        should_generate_video = mem0_service.should_generate_video(x_user_id, chat_request.message.content)
        logger.info(f"Should generate video: {should_generate_video}")
        
        # Check if audio should be generated based on user preferences
        should_generate_audio = mem0_service.should_generate_audio(x_user_id) or chat_request.requireAudio
        logger.info(f"Should generate audio: {should_generate_audio}")
        
        # Generate AI response with personalization
        logger.info(f"Calling generate_chat_response with is_quiz_request={should_generate_quiz}")
        ai_response = openai_service.generate_chat_response(
            user_message=chat_request.message.content,
            user_id=x_user_id,
            is_quiz_request=should_generate_quiz
        )
        logger.info(f"AI response received: {ai_response[:100]}...")
        
        # Personalize response with user's name
        ai_response = mem0_service.personalize_response(x_user_id, ai_response)
        
        # Generate quiz if requested
        quiz_questions = []
        if should_generate_quiz:
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
        
        # Generate video if requested
        video_data = None
        if should_generate_video:
            logger.info("Generating video for user request")
            try:
                # Extract video prompt from user message and AI response
                video_prompt = openai_service.extract_video_prompt(chat_request.message.content, ai_response)
                logger.info(f"Video prompt: {video_prompt}")
                
                # Generate video using OpenAI Sora 2
                video_result = await video_service.generate_video(
                    prompt=video_prompt,
                    model="sora-2",
                    size="1280x720",  # Horizontal format for desktop/web
                    seconds="12"  # Test with known supported duration
                )
                
                video_data = {
                    "videoId": video_result["id"],
                    "status": video_result["status"],
                    "prompt": video_prompt,
                    "size": video_result["size"],
                    "duration": video_result["seconds"]
                }
                
                logger.info(f"Video generation started with ID: {video_result['id']}")
                
            except Exception as video_error:
                logger.warning(f"Failed to generate video: {str(video_error)}")
                # Continue without video if generation fails
        
        # Generate response ID and timestamp
        response_id = str(uuid.uuid4())
        current_timestamp = datetime.now().isoformat()
        
        # Generate audio if requested
        audio_url = None
        if should_generate_audio:
            logger.info("Generating audio...")
            audio_base64 = elevenlabs_service.generate_audio(ai_response)
            if audio_base64:
                audio_url = f"data:audio/mpeg;base64,{audio_base64}"
                logger.info("Audio generated successfully")
            else:
                logger.warning("Failed to generate audio, falling back to mock URL")
                audio_url = "https://example.com/mock-audio.mp3"
        
        # Store session history in Mem0
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{response_id[:8]}"
        response_type = "text"
        if video_data:
            response_type = "video"
        elif quiz_questions:
            response_type = "quiz"
        elif audio_url:
            response_type = "audio"
        
        mem0_service.store_session_history(
            user_id=x_user_id,
            session_id=session_id,
            user_message=chat_request.message.content,
            ai_response=ai_response,
            response_type=response_type
        )
        
        # Build response
        response_data = {
            "responses": [
                {
                    "id": response_id,
                    "messageId": chat_request.message.id,
                    "content": ai_response,
                    "timestamp": current_timestamp,
                    "audioUrl": audio_url,
                    "videoUrl": f"/api/v1/video/{video_data['videoId']}" if video_data else None,
                    "video": video_data,
                    "quiz": quiz_questions,
                    "userContext": {
                        "userName": user_name,
                        "gradeLevel": grade_level,
                        "language": language,
                        "learningStyle": learning_style
                    }
                }
            ]
        }
        
        logger.info(f"Successfully generated response for user {x_user_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

# Video status endpoint
@app.get("/api/v1/video/{video_id}/status")
async def get_video_status(video_id: str):
    """Get the status of a video generation job"""
    try:
        status = await video_service.check_status(video_id)
        return {
            "success": True,
            "video": status
        }
    except Exception as e:
        logger.error(f"Error checking video status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking video status: {str(e)}")

# Video download endpoint
@app.get("/api/v1/video/{video_id}")
async def get_video(video_id: str):
    """Download a completed video"""
    try:
        # Check if video is completed
        status = await video_service.check_status(video_id)
        
        if status["status"] != "completed":
            return {
                "success": False,
                "message": f"Video is not ready yet. Status: {status['status']}",
                "status": status["status"],
                "progress": status.get("progress", 0)
            }
        
        # Download the video
        video_path = await video_service.download_video(video_id)
        
        if video_path and video_path.exists():
            return FileResponse(
                path=str(video_path),
                media_type="video/mp4",
                filename=f"{video_id}.mp4"
            )
        else:
            raise HTTPException(status_code=404, detail="Video file not found")
            
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

# List all videos endpoint
@app.get("/api/v1/videos")
async def list_videos():
    """List all generated videos"""
    try:
        videos = await video_service.list_videos()
        return {
            "success": True,
            "videos": videos,
            "count": len(videos)
        }
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing videos: {str(e)}")

# User preferences endpoints
@app.post("/api/v1/user/preferences")
async def set_user_preferences(
    preferences: dict,
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Set user preferences"""
    try:
        result = mem0_service.store_user_preferences(x_user_id, preferences)
        
        if result["success"]:
            return {
                "success": True,
                "message": "User preferences updated successfully",
                "preferences": preferences
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error setting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting user preferences: {str(e)}")

@app.get("/api/v1/user/preferences")
async def get_user_preferences(
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Get user preferences"""
    try:
        preferences = mem0_service.get_user_preferences(x_user_id)
        
        return {
            "success": True,
            "preferences": preferences
        }
            
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")

@app.get("/api/v1/user/context")
async def get_user_context(
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Get comprehensive user learning context"""
    try:
        context = mem0_service.get_learning_context(x_user_id)
        
        return {
            "success": True,
            "context": context
        }
            
    except Exception as e:
        logger.error(f"Error getting user context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user context: {str(e)}")

@app.get("/api/v1/user/session-history")
async def get_session_history(
    x_user_id: str = Header(..., alias="X-User-ID"),
    limit: int = 5
):
    """Get user session history"""
    try:
        history = mem0_service.get_session_history(x_user_id, limit)
        
        return {
            "success": True,
            "sessionHistory": history,
            "count": len(history)
        }
            
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting session history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
