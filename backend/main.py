from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
from datetime import datetime
import logging
import os
import shutil
from pathlib import Path

# Import our custom modules
from config import Config
from services import OpenAIService
from services.openai_video_service import OpenAIVideoService
from services import OpenAIService, ElevenLabsService
from services.mem0_service import Mem0Service
from services.supabase_mcp_service import SupabaseMCPService
from services.supabase_user_preferences_service import SupabaseUserPreferencesService
from services.intelligent_preference_extraction_service import IntelligentPreferenceExtractionService
from services.pdf_service import PDFService
from services.user_onboarding_service import UserOnboardingService
from models import ChatRequest, ChatResponse, ChatMessageResponse, QuizQuestion, FileUploadResponse, ChatMessage
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
supabase_preferences_service = SupabaseUserPreferencesService()
preference_extraction_service = IntelligentPreferenceExtractionService()
pdf_service = PDFService()
onboarding_service = UserOnboardingService()

# In-memory storage for onboarding session preferences (temporary)
onboarding_sessions = {}


# File upload configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

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
        success = supabase_preferences_service.store_user_preferences(x_user_id, preferences)
        
        if success:
            return {
                "success": True,
                "message": "User preferences updated successfully",
                "preferences": preferences
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store user preferences")
            
    except Exception as e:
        logger.error(f"Error setting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting user preferences: {str(e)}")

@app.get("/api/v1/user/preferences")
async def get_user_preferences(
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Get user preferences"""
    try:
        preferences = supabase_preferences_service.get_user_preferences(x_user_id)
        
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
        preferences = supabase_preferences_service.get_user_preferences(x_user_id)
        
        context = {
            "user_name": preferences.get("name", "Student"),
            "grade_level": preferences.get("grade_level", "middle"),
            "language": preferences.get("language", "en"),
            "learning_style": preferences.get("learning_style", "reading"),
            "preferred_subjects": preferences.get("preferred_subjects", []),
            "preferences": preferences
        }
        
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

# File upload endpoint
@app.post("/api/v1/upload/file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Upload a PDF file for use in chat"""
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not allowed. Only PDF files are supported."
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"File uploaded successfully: {file.filename} -> {file_path}")
        
        return FileUploadResponse(
            success=True,
            fileId=file_id,
            fileName=file.filename,
            filePath=str(file_path),
            fileSize=len(file_content),
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

# File download endpoint
@app.get("/api/v1/files/{file_id}")
async def get_file(file_id: str):
    """Download an uploaded file"""
    try:
        # Find the file by ID
        file_path = None
        for file in UPLOAD_DIR.iterdir():
            if file.name.startswith(file_id):
                file_path = file
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=file_path.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

# List uploaded files endpoint
@app.get("/api/v1/files")
async def list_files(x_user_id: str = Header(..., alias="X-User-ID")):
    """List all uploaded files for a user"""
    try:
        files = []
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == ".pdf":
                file_id = file_path.stem.split("_")[0]  # Extract file ID from filename
                files.append({
                    "fileId": file_id,
                    "fileName": file_path.name,
                    "fileSize": file_path.stat().st_size,
                    "uploadedAt": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                })
        
        return {
            "success": True,
            "files": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

# Enhanced chat endpoint with knowledge graph integration
@app.post("/api/v1/chat/message")
async def chat_message(
    message: str = Form(...),
    message_id: str = Form(...),
    user_id: str = Form(...),
    timestamp: str = Form(...),
    require_audio: bool = Form(False),
    attached_file: UploadFile = File(None),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """Process user chat message and return AI response with optional audio/video/quiz"""
    try:
        # Handle file upload if provided
        attached_file_path = None
        if attached_file and attached_file.filename:
            # Validate file type
            file_extension = Path(attached_file.filename).suffix.lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type {file_extension} not allowed. Only PDF files are supported."
                )
            
            # Save the attached file
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{attached_file.filename}"
            file_path = UPLOAD_DIR / safe_filename
            
            file_content = await attached_file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            attached_file_path = str(file_path)
            logger.info(f"Attached file saved: {attached_file.filename} -> {file_path}")
        
        # Create ChatMessage object
        chat_message_obj = ChatMessage(
            id=message_id,
            userId=user_id,
            content=message,
            timestamp=timestamp
        )
        
        # Create ChatRequest object
        chat_request = ChatRequest(
            message=chat_message_obj,
            requireAudio=require_audio,
            attachedFile=attached_file_path
        )
        
        logger.info(f"Processing chat message from user {x_user_id}: {message}")
        if attached_file_path:
            logger.info(f"Message includes attached file: {attached_file_path}")
        
        # Generate audiobook if PDF file is attached
        audiobook_chunks = None
        audiobook_info = None
        if attached_file_path and attached_file_path.endswith('.pdf'):
            logger.info("PDF file detected, generating audiobook...")
            try:
                # Extract text from PDF
                extracted_text = pdf_service.extract_text_from_pdf(attached_file_path)
                if extracted_text:
                    # Clean the extracted text
                    cleaned_text = pdf_service.clean_extracted_text(extracted_text)
                    logger.info(f"Extracted {len(cleaned_text)} characters from PDF")
                    
                    # Generate audiobook using ElevenLabs
                    audiobook_chunks = elevenlabs_service.generate_audiobook(cleaned_text)
                    
                    if audiobook_chunks:
                        # Get PDF info for audiobook metadata
                        pdf_info = pdf_service.get_pdf_info(attached_file_path)
                        audiobook_info = {
                            "fileName": attached_file.filename,
                            "totalChunks": len(audiobook_chunks),
                            "textLength": len(cleaned_text),
                            "pdfInfo": pdf_info
                        }
                        logger.info(f"Successfully generated audiobook with {len(audiobook_chunks)} chunks")
                    else:
                        logger.warning("Failed to generate audiobook from PDF")
                else:
                    logger.warning("Failed to extract text from PDF")
            except Exception as audiobook_error:
                logger.error(f"Error generating audiobook: {str(audiobook_error)}")
        
        # Get user preferences from Supabase
        user_preferences = supabase_preferences_service.get_user_preferences(x_user_id)
        user_name = user_preferences.get("name", "Student")
        grade_level = user_preferences.get("grade_level", "middle")
        language = user_preferences.get("language", "en")
        learning_style = user_preferences.get("learning_style", "reading")
        
        # Extract any new preferences from the current message using OpenAI
        extracted_preferences = preference_extraction_service.extract_preferences_from_message(message, user_preferences)
        
        # Merge extracted preferences with existing ones
        if extracted_preferences:
            user_preferences = preference_extraction_service.merge_preferences(user_preferences, extracted_preferences)
            # Update preferences in Supabase
            supabase_preferences_service.update_user_preferences(x_user_id, extracted_preferences)
            # Update local variables
            user_name = user_preferences.get("name", user_name)
            grade_level = user_preferences.get("grade_level", grade_level)
            language = user_preferences.get("language", language)
            learning_style = user_preferences.get("learning_style", learning_style)
        
        # Check if user needs onboarding (but skip if audiobook was generated)
        needs_onboarding = onboarding_service.should_start_onboarding(user_preferences) and not audiobook_chunks
        logger.info(f"User needs onboarding: {needs_onboarding}")
        
        if needs_onboarding:
            # Handle onboarding flow
            logger.info("Starting user onboarding flow")
            
            # Get any previously collected preferences from this session (stored in memory)
            session_preferences = onboarding_sessions.get(x_user_id, {})
            
            # Generate onboarding response
            onboarding_result = onboarding_service.get_onboarding_response(
                user_message=message,
                user_preferences=user_preferences,
                collected_preferences=session_preferences
            )
            
            if onboarding_result["is_complete"]:
                # Onboarding complete, save preferences and continue with normal flow
                logger.info("Onboarding completed, saving preferences")
                merged_preferences = onboarding_service.merge_preferences(
                    user_preferences, 
                    onboarding_result["collected_preferences"]
                )
                
                # Save the complete preferences to Supabase
                supabase_preferences_service.store_user_preferences(x_user_id, merged_preferences)
                
                # Update local variables with new preferences
                user_preferences = merged_preferences
                user_name = user_preferences.get("name", "Student")
                grade_level = user_preferences.get("grade", "middle")
                language = user_preferences.get("language", "en")
                learning_style = user_preferences.get("learning_style", "reading")
                
                # Clear session preferences since onboarding is complete
                if x_user_id in onboarding_sessions:
                    del onboarding_sessions[x_user_id]
                
                logger.info(f"Updated user context - Name: {user_name}, Grade: {grade_level}, Language: {language}, Learning Style: {learning_style}")
            else:
                # Still in onboarding, save current progress and return onboarding response
                logger.info(f"Onboarding in progress, step: {onboarding_result['current_step']}")
                
                # Save current progress to in-memory session preferences
                onboarding_sessions[x_user_id] = onboarding_result["collected_preferences"]
                
                # Return onboarding response in standardized format
                response_id = str(uuid.uuid4())
                current_timestamp = datetime.now().isoformat()
                
                return {
                    "responses": [
                        {
                            "id": response_id,
                            "messageId": message_id,
                            "content": onboarding_result["response"],
                            "timestamp": current_timestamp,
                            "audioUrl": None,
                            "audiobookChunks": None,
                            "audiobookInfo": None,
                            "videoUrl": None,
                            "video": None,
                            "quiz": None,
                            "studyMaterials": [],
                            "recommendationDetected": False,
                            "addedMaterial": None,
                            "hasSupabaseRecommendations": False,
                            "attachedFile": None,
                            "userContext": {
                                "userName": user_name,
                                "gradeLevel": grade_level,
                                "language": language,
                                "learningStyle": learning_style,
                                "isOnboarding": True,
                                "onboardingStep": onboarding_result["current_step"]
                            }
                        }
                    ]
                }
        
        logger.info(f"User context - Name: {user_name}, Grade: {grade_level}, Language: {language}, Learning Style: {learning_style}")
        
        # Check if user requested a quiz
        should_generate_quiz = openai_service.should_generate_quiz(chat_request.message.content)
        logger.info(f"Is quiz request: {should_generate_quiz}")
        
        # Check if video should be generated based on user preferences and message
        should_generate_video = supabase_preferences_service.should_generate_video(x_user_id, chat_request.message.content)
        logger.info(f"Should generate video: {should_generate_video}")
        
        # Check if audio should be generated based on user preferences
        should_generate_audio = supabase_preferences_service.should_generate_audio(x_user_id) or chat_request.requireAudio
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
            # Get chat history from Supabase for context
            chat_history = []
            if supabase_mcp_service.is_available():
                try:
                    chat_history = supabase_mcp_service.get_user_chat_history(x_user_id, limit=5)
                    logger.info(f"Retrieved {len(chat_history)} previous messages for context")
                except Exception as history_error:
                    logger.warning(f"Failed to get chat history: {str(history_error)}")
                    chat_history = []
            
            logger.info(f"Calling generate_chat_response with is_quiz_request={should_generate_quiz}, chat_history={len(chat_history)} messages")
            ai_response = openai_service.generate_chat_response(
                user_message=chat_request.message.content,
                user_id=x_user_id,
                is_quiz_request=should_generate_quiz,
                chat_history=chat_history
            )
            logger.info(f"AI response received: {ai_response[:100]}...")
            
            # Personalize response with user's name
            ai_response = supabase_preferences_service.personalize_response(x_user_id, ai_response)
        
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
                    "audiobookChunks": audiobook_chunks,
                    "audiobookInfo": audiobook_info,
                    "videoUrl": f"/api/v1/video/{video_data['videoId']}" if video_data else None,
                    "video": video_data,
                    "quiz": quiz_questions,
                    "studyMaterials": study_materials,
                    "recommendationDetected": recommendation_result.get("recommendation_detected", False) if recommendation_result else False,
                    "addedMaterial": recommendation_result.get("material") if recommendation_result and recommendation_result.get("recommendation_detected") else None,
                    "hasSupabaseRecommendations": has_supabase_recommendations,
                    "attachedFile": {
                        "filePath": attached_file_path,
                        "fileName": attached_file.filename if attached_file and attached_file.filename else None
                    } if attached_file_path else None,
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
