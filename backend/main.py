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
from services.supabase_mcp_service import SupabaseMCPService
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
supabase_mcp_service = SupabaseMCPService()

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

# Knowledge Graph Endpoints
@app.post("/api/v1/knowledge-graph/study-material")
async def add_study_material(
    material_data: dict,
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Add a study material to the knowledge graph"""
    try:
        # Extract material information from the request
        title = material_data.get("title")
        material_type = material_data.get("type", "book")
        subject = material_data.get("subject")
        description = material_data.get("description")
        url = material_data.get("url")
        author = material_data.get("author")
        grade_level = material_data.get("grade_level")
        rating = material_data.get("rating")
        tags = material_data.get("tags", [])
        
        if not title or not subject:
            raise HTTPException(status_code=400, detail="Title and subject are required")
        
        result = supabase_mcp_service.add_study_material(
            title=title,
            material_type=material_type,
            subject=subject,
            recommended_by=x_user_id,
            description=description,
            url=url,
            author=author,
            grade_level=grade_level,
            rating=rating,
            tags=tags
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "material": result["material"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error adding study material: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding study material: {str(e)}")

@app.get("/api/v1/knowledge-graph/study-materials")
async def get_study_materials(
    subject: str = None,
    grade_level: str = None,
    material_type: str = None,
    limit: int = 10
):
    """Get study material recommendations"""
    try:
        if not subject:
            raise HTTPException(status_code=400, detail="Subject parameter is required")
        
        materials = supabase_mcp_service.get_study_recommendations(
            subject=subject,
            grade_level=grade_level,
            material_type=material_type,
            limit=limit
        )
        
        return {
            "success": True,
            "materials": materials,
            "count": len(materials),
            "filters": {
                "subject": subject,
                "grade_level": grade_level,
                "material_type": material_type
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting study materials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting study materials: {str(e)}")

@app.get("/api/v1/knowledge-graph/learning-patterns")
async def get_learning_patterns(
    x_user_id: str = Header(..., alias="X-User-ID"),
    limit: int = 20
):
    """Get user's learning patterns and suggestions"""
    try:
        patterns = supabase_mcp_service.get_user_learning_patterns(x_user_id, limit)
        
        if patterns["success"]:
            return {
                "success": True,
                "patterns": patterns["patterns"]
            }
        else:
            raise HTTPException(status_code=500, detail=patterns["error"])
            
    except Exception as e:
        logger.error(f"Error getting learning patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting learning patterns: {str(e)}")

@app.get("/api/v1/knowledge-graph/search")
async def search_materials(
    query: str,
    limit: int = 5
):
    """Search for study materials"""
    try:
        materials = supabase_mcp_service.search_similar_materials(query, limit)
        
        return {
            "success": True,
            "materials": materials,
            "count": len(materials),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching materials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching materials: {str(e)}")

@app.post("/api/v1/knowledge-graph/initialize")
async def initialize_knowledge_graph():
    """Initialize the knowledge graph tables"""
    try:
        success = supabase_mcp_service.create_knowledge_graph_tables()
        
        if success:
            return {
                "success": True,
                "message": "Knowledge graph tables created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create knowledge graph tables")
            
    except Exception as e:
        logger.error(f"Error initializing knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initializing knowledge graph: {str(e)}")

# Enhanced chat endpoint with knowledge graph integration
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
        
        # Check if user is asking for study material recommendations
        is_material_request = any(keyword in chat_request.message.content.lower() for keyword in [
            "book", "recommend", "study material", "resource", "learn", "read", "watch", "course"
        ])
        logger.info(f"Is material request: {is_material_request}")
        logger.info(f"Message content: {chat_request.message.content}")
        
        # Check for Supabase recommendations first if this is a material request
        study_materials = []
        has_supabase_recommendations = False
        ai_response = ""
        
        logger.info(f"Supabase service available: {supabase_mcp_service.is_available()}")
        print(f"DEBUG: is_material_request={is_material_request}, supabase_available={supabase_mcp_service.is_available()}")
        if is_material_request and supabase_mcp_service.is_available():
            try:
                # Extract subject from the message
                subject = None
                message_lower = chat_request.message.content.lower()
                if "physics" in message_lower:
                    subject = "physics"
                elif "chemistry" in message_lower:
                    subject = "chemistry"
                elif "biology" in message_lower:
                    subject = "biology"
                elif "math" in message_lower:
                    subject = "mathematics"
                elif "history" in message_lower:
                    subject = "history"
                
                if subject:
                    # First try with specific grade level
                    study_materials = supabase_mcp_service.get_study_recommendations(
                        subject=subject,
                        grade_level=grade_level,
                        limit=3
                    )
                    
                    # If no materials found with specific grade level, try without grade filter
                    if not study_materials or len(study_materials) == 0:
                        logger.info(f"No materials found for {subject} at {grade_level} level, trying without grade filter")
                        study_materials = supabase_mcp_service.get_study_recommendations(
                            subject=subject,
                            grade_level=None,  # No grade level filter
                            limit=3
                        )
                    
                    # Check if we found recommendations in Supabase
                    if study_materials and len(study_materials) > 0:
                        has_supabase_recommendations = True
                        logger.info(f"Found {len(study_materials)} Supabase recommendations for {subject}")
                        
                        # Generate a personalized response based on Supabase recommendations
                        ai_response = f"Great question! I found some excellent {subject} resources that our community of learners has highly recommended:\n\n"
                        
                        for i, material in enumerate(study_materials, 1):
                            # Fix the rating stars generation to handle None values
                            rating = material.get('rating', 0)
                            if rating is None:
                                rating = 0
                            rating_stars = "⭐" * int(rating)
                            
                            grade_info = f" (Grade: {material.get('grade_level', 'All levels')})" if material.get('grade_level') else ""
                            author_info = f" by {material.get('author', 'Unknown')}" if material.get('author') else ""
                            url_info = f"\n🔗 Link: {material.get('url')}" if material.get('url') else ""
                            tags_info = f"\n🏷️ Tags: {', '.join(material.get('tags', []))}" if material.get('tags') else ""
                            
                            ai_response += f"{i}. **{material.get('title', 'Unknown Title')}**{author_info}{grade_info}\n"
                            ai_response += f"   📚 Type: {material.get('type', 'Unknown').title()}\n"
                            ai_response += f"   ⭐ Rating: {rating_stars} ({rating}/5)\n"
                            ai_response += f"   📝 Description: {material.get('description', 'No description available')}{url_info}{tags_info}\n\n"
                        
                        ai_response += f"These are real recommendations from students who have used these resources to learn {subject}. "
                        ai_response += f"Each one has been tried and tested by our community! Would you like me to explain more about any of these, or do you have questions about specific {subject} topics?"
                        
                    else:
                        logger.info(f"No Supabase recommendations found for {subject}, using AI fallback")
                        
            except Exception as material_error:
                logger.warning(f"Failed to get study materials: {str(material_error)}")
        
        # Generate AI response only if we don't have Supabase recommendations
        if not has_supabase_recommendations:
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
                    size="720x1280",  # Vertical format for mobile
                    seconds="8"
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
        
        # Process chat for automatic recommendation detection and store in Supabase knowledge graph
        recommendation_result = None
        if supabase_mcp_service.is_available():
            try:
                # First, check if user is recommending a material
                recommendation_result = supabase_mcp_service.process_chat_for_recommendations(
                    user_id=x_user_id,
                    message=chat_request.message.content
                )
                
                if recommendation_result.get("recommendation_detected"):
                    logger.info(f"Auto-detected recommendation from user {x_user_id}")
                
                # Extract subject from the conversation for learning history
                subject = None
                if "physics" in chat_request.message.content.lower():
                    subject = "physics"
                elif "chemistry" in chat_request.message.content.lower():
                    subject = "chemistry"
                elif "biology" in chat_request.message.content.lower():
                    subject = "biology"
                elif "math" in chat_request.message.content.lower():
                    subject = "mathematics"
                elif "history" in chat_request.message.content.lower():
                    subject = "history"
                
                # Store learning history
                supabase_mcp_service.add_user_learning_history(
                    user_id=x_user_id,
                    question=chat_request.message.content,
                    response=ai_response,
                    response_type=response_type,
                    subject=subject
                )
            except Exception as kg_error:
                logger.warning(f"Failed to store in knowledge graph: {str(kg_error)}")
        
        
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
                    "studyMaterials": study_materials,
                    "recommendationDetected": recommendation_result.get("recommendation_detected", False) if recommendation_result else False,
                    "addedMaterial": recommendation_result.get("material") if recommendation_result and recommendation_result.get("recommendation_detected") else None,
                    "hasSupabaseRecommendations": has_supabase_recommendations,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
