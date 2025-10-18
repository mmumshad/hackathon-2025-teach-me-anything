# Backend Development Plan - TechMeAnything ⚙️

## Developer: Ram
## Timeline: 24-Hour Hackathon Sprint
## Tech Stack: FastAPI + Python + AI Services

---

## Phase 1: Project Setup (Hours 1-3) ⚙️

### Hour 1: FastAPI Initialization
- [ ] **Initialize FastAPI project**
  ```bash
  mkdir backend
  cd backend
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install fastapi uvicorn python-dotenv
  ```
- [ ] **Create basic project structure**
  ```
  backend/
  ├── main.py              # FastAPI app
  ├── models/              # Pydantic models
  │   ├── __init__.py
  │   ├── chat.py
  │   └── user.py
  ├── services/            # Business logic
  │   ├── __init__.py
  │   ├── ai_service.py
  │   ├── mem0_service.py
  │   └── tts_service.py
  ├── utils/               # Utility functions
  │   ├── __init__.py
  │   └── helpers.py
  ├── requirements.txt
  └── .env
  ```

### Hour 2: Environment & Dependencies
- [ ] **Install required packages**
  ```bash
  pip install fastapi uvicorn python-dotenv
  pip install openai elevenlabs-python google-generativeai
  pip install mem0ai requests httpx
  pip install python-multipart
  ```
- [ ] **Set up environment variables**
  ```bash
  # .env
  OPENAI_API_KEY=your_openai_api_key
  ELEVENLABS_API_KEY=your_elevenlabs_api_key
  GEMINI_API_KEY=your_gemini_api_key
  MEM0_API_KEY=your_mem0_api_key
  MAX_VIDEO_DURATION=60
  DEFAULT_LANGUAGE=en
  ```
- [ ] **Create requirements.txt**
  ```
  fastapi==0.104.1
  uvicorn==0.24.0
  python-dotenv==1.0.0
  openai==1.3.0
  elevenlabs-python==0.2.26
  google-generativeai==0.3.0
  mem0ai==0.0.7
  requests==2.31.0
  httpx==0.25.0
  python-multipart==0.0.6
  ```

### Hour 3: Basic API Structure
- [ ] **Create main FastAPI app**
  ```python
  # main.py
  from fastapi import FastAPI, HTTPException, Header
  from fastapi.middleware.cors import CORSMiddleware
  from dotenv import load_dotenv
  import os
  
  load_dotenv()
  
  app = FastAPI(title="TechMeAnything API", version="1.0.0")
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  
  @app.get("/health")
  async def health_check():
      return {"status": "healthy", "message": "API is running"}
  
  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8000)
  ```
- [ ] **Test basic server**
  ```bash
  python main.py
  # Test: curl http://localhost:8000/health
  ```

---

## Phase 2: Data Models & API Contracts (Hours 4-6) 📋

### Hour 4: Pydantic Models
- [ ] **Create chat models**
  ```python
  # models/chat.py
  from pydantic import BaseModel
  from typing import Optional, List
  from datetime import datetime
  
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
  ```

### Hour 5: User Models
- [ ] **Create user models**
  ```python
  # models/user.py
  from pydantic import BaseModel
  from typing import List, Optional
  from datetime import datetime
  
  class UserPreferences(BaseModel):
      language: str = "en"
      muteAudio: bool = True
      learningLevel: str = "beginner"  # beginner, intermediate, advanced
      learningStyle: str = "visual"    # visual, auditory, kinesthetic
      preferredSubjects: List[str] = []
  
  class UserProfile(BaseModel):
      userId: str
      userName: str
      gradeLevel: int
      preferences: UserPreferences
      createdAt: str
      lastActiveAt: str
  ```

### Hour 6: API Endpoint Structure
- [ ] **Create main chat endpoint**
  ```python
  # main.py
  from models.chat import ChatRequest, ChatMessageResponse
  from services.ai_service import AIService
  from services.mem0_service import Mem0Service
  
  @app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
  async def chat_message(
      chat_request: ChatRequest,
      x_user_id: str = Header(..., alias="X-User-ID")
  ):
      try:
          # Process chat message
          ai_service = AIService()
          mem0_service = Mem0Service()
          
          # Get user profile from Mem0
          user_profile = await mem0_service.get_user_profile(x_user_id)
          
          # Generate AI response
          response = await ai_service.generate_response(
              chat_request.message.content,
              user_profile
          )
          
          return response
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  ```

---

## Phase 3: Mem0 Integration (Hours 7-9) 🗄️

### Hour 7: Mem0 Service Setup
- [ ] **Create Mem0 service**
  ```python
  # services/mem0_service.py
  import os
  from mem0 import Memory
  from models.user import UserProfile, UserPreferences
  
  class Mem0Service:
      def __init__(self):
          self.memory = Memory(config={
              "MEM0_API_KEY": os.getenv("MEM0_API_KEY")
          })
      
      async def get_user_profile(self, user_id: str) -> UserProfile:
          """Get user profile from Mem0"""
          try:
              profile_data = self.memory.get(user_id)
              if not profile_data:
                  # Create default profile
                  return self._create_default_profile(user_id)
              return UserProfile(**profile_data)
          except Exception as e:
              print(f"Error getting user profile: {e}")
              return self._create_default_profile(user_id)
      
      async def update_user_profile(self, user_id: str, profile: UserProfile):
          """Update user profile in Mem0"""
          try:
              self.memory.put(user_id, profile.dict())
          except Exception as e:
              print(f"Error updating user profile: {e}")
      
      def _create_default_profile(self, user_id: str) -> UserProfile:
          """Create default user profile"""
          return UserProfile(
              userId=user_id,
              userName="Student",
              gradeLevel=5,
              preferences=UserPreferences(),
              createdAt=datetime.now().isoformat(),
              lastActiveAt=datetime.now().isoformat()
          )
  ```

### Hour 8: User Profile Management
- [ ] **Implement profile updates**
  ```python
  # services/mem0_service.py
  async def update_user_language(self, user_id: str, language: str):
      """Update user language preference"""
      profile = await self.get_user_profile(user_id)
      profile.preferences.language = language
      profile.lastActiveAt = datetime.now().isoformat()
      await self.update_user_profile(user_id, profile)
  
  async def update_user_assessment(self, user_id: str, assessment_data: dict):
      """Update user assessment data"""
      profile = await self.get_user_profile(user_id)
      # Update profile based on assessment
      profile.lastActiveAt = datetime.now().isoformat()
      await self.update_user_profile(user_id, profile)
  ```

### Hour 9: Conversation History
- [ ] **Store conversation history**
  ```python
  # services/mem0_service.py
  async def store_conversation(self, user_id: str, message: str, response: str):
      """Store conversation in Mem0"""
      try:
          conversation_key = f"{user_id}_conversation"
          conversation_data = {
              "message": message,
              "response": response,
              "timestamp": datetime.now().isoformat()
          }
          self.memory.put(conversation_key, conversation_data)
      except Exception as e:
          print(f"Error storing conversation: {e}")
  
  async def get_conversation_history(self, user_id: str) -> List[dict]:
      """Get conversation history"""
      try:
          conversation_key = f"{user_id}_conversation"
          history = self.memory.get(conversation_key)
          return history if history else []
      except Exception as e:
          print(f"Error getting conversation history: {e}")
          return []
  ```

---

## Phase 4: OpenAI Integration (Hours 10-12) 🤖

### Hour 10: OpenAI Service Setup
- [ ] **Create OpenAI service**
  ```python
  # services/ai_service.py
  import os
  from openai import OpenAI
  from models.chat import ChatResponse, QuizQuestion, QuizOption
  from models.user import UserProfile
  import uuid
  from datetime import datetime
  
  class AIService:
      def __init__(self):
          self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
      
      async def generate_response(
          self, 
          user_message: str, 
          user_profile: UserProfile
      ) -> ChatResponse:
          """Generate AI response based on user message and profile"""
          try:
              # Create personalized prompt
              prompt = self._create_prompt(user_message, user_profile)
              
              # Call OpenAI API
              response = self.client.chat.completions.create(
                  model="gpt-4",
                  messages=[
                      {"role": "system", "content": prompt},
                      {"role": "user", "content": user_message}
                  ],
                  max_tokens=500,
                  temperature=0.7
              )
              
              # Process response
              ai_content = response.choices[0].message.content
              
              return ChatResponse(
                  id=str(uuid.uuid4()),
                  messageId="user-message-id",
                  content=ai_content,
                  timestamp=datetime.now().isoformat()
              )
          except Exception as e:
              print(f"Error generating AI response: {e}")
              return self._create_fallback_response()
  ```

### Hour 11: Personalized Responses
- [ ] **Implement personalization**
  ```python
  # services/ai_service.py
  def _create_prompt(self, user_message: str, user_profile: UserProfile) -> str:
      """Create personalized prompt based on user profile"""
      prompt = f"""
      You are an AI tutor for a {user_profile.gradeLevel}th grade student named {user_profile.userName}.
      
      Student Profile:
      - Grade Level: {user_profile.gradeLevel}
      - Learning Level: {user_profile.preferences.learningLevel}
      - Learning Style: {user_profile.preferences.learningStyle}
      - Preferred Subjects: {', '.join(user_profile.preferences.preferredSubjects)}
      - Language: {user_profile.preferences.language}
      
      Instructions:
      - Respond in a way appropriate for their grade level
      - Use their preferred learning style
      - Be encouraging and supportive
      - If the topic is educational, consider creating a quiz
      - Keep responses concise but informative
      """
      return prompt
  
  async def generate_quiz(self, topic: str, user_profile: UserProfile) -> List[QuizQuestion]:
      """Generate quiz questions for educational topics"""
      try:
          prompt = f"""
          Create 2 quiz questions about: {topic}
          For a {user_profile.gradeLevel}th grade student.
          Each question should have 4 options (a, b, c, d).
          Return in JSON format with questions, options, correct answers, and explanations.
          """
          
          response = self.client.chat.completions.create(
              model="gpt-4",
              messages=[{"role": "user", "content": prompt}],
              max_tokens=800,
              temperature=0.3
          )
          
          # Parse response and create quiz questions
          return self._parse_quiz_response(response.choices[0].message.content)
      except Exception as e:
          print(f"Error generating quiz: {e}")
          return []
  ```

### Hour 12: Language Detection
- [ ] **Implement language detection**
  ```python
  # services/ai_service.py
  async def detect_language(self, text: str) -> str:
      """Detect language from user input"""
      try:
          prompt = f"""
          Detect the language of this text: "{text}"
          Return only the language code (en, zh, hi, es, ar).
          """
          
          response = self.client.chat.completions.create(
              model="gpt-4",
              messages=[{"role": "user", "content": prompt}],
              max_tokens=10,
              temperature=0.1
          )
          
          detected_language = response.choices[0].message.content.strip()
          return detected_language if detected_language in ['en', 'zh', 'hi', 'es', 'ar'] else 'en'
      except Exception as e:
          print(f"Error detecting language: {e}")
          return 'en'
  ```

---

## Phase 5: ElevenLabs TTS Integration (Hours 13-15) 🎵

### Hour 13: ElevenLabs Service Setup
- [ ] **Create TTS service**
  ```python
  # services/tts_service.py
  import os
  from elevenlabs import generate, save
  import tempfile
  from typing import Optional
  
  class TTSService:
      def __init__(self):
          self.api_key = os.getenv("ELEVENLABS_API_KEY")
          self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice
      
      async def generate_audio(self, text: str, language: str = "en") -> Optional[str]:
          """Generate audio from text using ElevenLabs"""
          try:
              # Select voice based on language
              voice_id = self._get_voice_for_language(language)
              
              # Generate audio
              audio = generate(
                  text=text,
                  voice=voice_id,
                  model="eleven_multilingual_v2"
              )
              
              # Save to temporary file
              with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                  save(audio, tmp_file.name)
                  return tmp_file.name
          except Exception as e:
              print(f"Error generating audio: {e}")
              return None
      
      def _get_voice_for_language(self, language: str) -> str:
          """Get appropriate voice for language"""
          voice_mapping = {
              "en": "21m00Tcm4TlvDq8ikWAM",  # English
              "zh": "21m00Tcm4TlvDq8ikWAM",  # Chinese (use English voice for now)
              "hi": "21m00Tcm4TlvDq8ikWAM",  # Hindi (use English voice for now)
              "es": "21m00Tcm4TlvDq8ikWAM",  # Spanish (use English voice for now)
              "ar": "21m00Tcm4TlvDq8ikWAM"   # Arabic (use English voice for now)
          }
          return voice_mapping.get(language, "21m00Tcm4TlvDq8ikWAM")
  ```

### Hour 14: Audio Integration
- [ ] **Integrate TTS with chat**
  ```python
  # main.py
  from services.tts_service import TTSService
  
  @app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
  async def chat_message(
      chat_request: ChatRequest,
      x_user_id: str = Header(..., alias="X-User-ID")
  ):
      try:
          # Generate AI response
          ai_service = AIService()
          mem0_service = Mem0Service()
          
          user_profile = await mem0_service.get_user_profile(x_user_id)
          response = await ai_service.generate_response(
              chat_request.message.content,
              user_profile
          )
          
          # Generate audio if requested
          audio_url = None
          if chat_request.requireAudio:
              tts_service = TTSService()
              audio_file = await tts_service.generate_audio(
                  response.content,
                  user_profile.preferences.language
              )
              if audio_file:
                  audio_url = f"/audio/{response.id}.mp3"
                  # Serve audio file (implement file serving)
          
          return ChatMessageResponse(
              success=True,
              response=response,
              audioUrl=audio_url
          )
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  ```

### Hour 15: Audio File Serving
- [ ] **Implement audio file serving**
  ```python
  # main.py
  from fastapi.staticfiles import StaticFiles
  import os
  
  # Create audio directory
  os.makedirs("audio", exist_ok=True)
  
  @app.get("/audio/{filename}")
  async def serve_audio(filename: str):
      """Serve audio files"""
      audio_path = f"audio/{filename}"
      if os.path.exists(audio_path):
          return FileResponse(audio_path, media_type="audio/mpeg")
      else:
          raise HTTPException(status_code=404, detail="Audio file not found")
  ```

---

## Phase 6: Video Generation (Hours 16-18) 🎬

### Hour 16: Video Service Setup
- [ ] **Create video service**
  ```python
  # services/video_service.py
  import os
  import google.generativeai as genai
  from typing import Optional
  
  class VideoService:
      def __init__(self):
          genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
          self.model = genai.GenerativeModel('gemini-pro')
      
      async def generate_video_script(self, topic: str, user_profile: UserProfile) -> str:
          """Generate video script for educational content"""
          try:
              prompt = f"""
              Create a 30-second educational video script about: {topic}
              For a {user_profile.gradeLevel}th grade student.
              Keep it to maximum 10 sentences.
              Make it engaging and educational.
              """
              
              response = self.model.generate_content(prompt)
              return response.text
          except Exception as e:
              print(f"Error generating video script: {e}")
              return f"Educational content about {topic}"
      
      async def generate_video(self, script: str, topic: str) -> Optional[str]:
          """Generate video using Gemini (fallback)"""
          try:
              # For MVP, return a placeholder video URL
              # In production, this would integrate with Sora 2 or similar
              return f"https://mock-video.com/{topic.replace(' ', '_')}.mp4"
          except Exception as e:
              print(f"Error generating video: {e}")
              return None
  ```

### Hour 17: Video Integration
- [ ] **Integrate video with chat**
  ```python
  # main.py
  from services.video_service import VideoService
  
  @app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
  async def chat_message(
      chat_request: ChatRequest,
      x_user_id: str = Header(..., alias="X-User-ID")
  ):
      try:
          # Generate AI response
          ai_service = AIService()
          mem0_service = Mem0Service()
          video_service = VideoService()
          
          user_profile = await mem0_service.get_user_profile(x_user_id)
          response = await ai_service.generate_response(
              chat_request.message.content,
              user_profile
          )
          
          # Check if video should be generated
          video_url = None
          if self._should_generate_video(chat_request.message.content):
              script = await video_service.generate_video_script(
                  chat_request.message.content,
                  user_profile
              )
              video_url = await video_service.generate_video(
                  script,
                  chat_request.message.content
              )
          
          return ChatMessageResponse(
              success=True,
              response=response,
              videoUrl=video_url
          )
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  
  def _should_generate_video(self, content: str) -> bool:
      """Determine if video should be generated"""
      educational_keywords = [
          "explain", "how", "what", "why", "photosynthesis", 
          "math", "science", "history", "learn", "teach"
      ]
      return any(keyword in content.lower() for keyword in educational_keywords)
  ```

### Hour 18: Video Optimization
- [ ] **Optimize video generation**
  ```python
  # services/video_service.py
  async def generate_educational_video(
      self, 
      topic: str, 
      user_profile: UserProfile
  ) -> dict:
      """Generate complete educational video package"""
      try:
          # Generate script
          script = await self.generate_video_script(topic, user_profile)
          
          # Generate video (placeholder for MVP)
          video_url = await self.generate_video(script, topic)
          
          # Generate quiz questions
          ai_service = AIService()
          quiz = await ai_service.generate_quiz(topic, user_profile)
          
          return {
              "script": script,
              "videoUrl": video_url,
              "quiz": quiz
          }
      except Exception as e:
          print(f"Error generating educational video: {e}")
          return {"script": "", "videoUrl": None, "quiz": []}
  ```

---

## Phase 7: Testing & Integration (Hours 19-24) 🧪

### Hours 19-20: API Testing
- [ ] **Test all endpoints**
  ```bash
  # Test health endpoint
  curl http://localhost:8000/health
  
  # Test chat endpoint
  curl -X POST "http://localhost:8000/api/v1/chat/message" \
    -H "Content-Type: application/json" \
    -H "X-User-ID: test-user-123" \
    -d '{
      "message": {
        "id": "msg-1",
        "userId": "test-user-123",
        "content": "Tell me about photosynthesis",
        "timestamp": "2024-01-01T00:00:00Z"
      },
      "requireAudio": true
    }'
  ```
- [ ] **Fix critical bugs**
  - Error handling
  - API response format
  - CORS issues
  - Authentication

### Hours 21-22: Performance Optimization
- [ ] **Optimize API performance**
  - Response time optimization
  - Memory usage
  - Error handling
  - Logging
- [ ] **Add monitoring**
  ```python
  # utils/helpers.py
  import logging
  import time
  
  def log_api_call(func):
      def wrapper(*args, **kwargs):
          start_time = time.time()
          result = func(*args, **kwargs)
          end_time = time.time()
          logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
          return result
      return wrapper
  ```

### Hours 23-24: Final Testing & Documentation
- [ ] **End-to-end testing**
  - Complete user flow
  - All AI integrations
  - Error scenarios
  - Performance testing
- [ ] **Create API documentation**
  ```python
  # main.py
  app = FastAPI(
      title="TechMeAnything API",
      description="AI-powered educational platform API",
      version="1.0.0",
      docs_url="/docs",
      redoc_url="/redoc"
  )
  ```

---

## Key Services to Build 🔧

### Core Services
- [ ] `Mem0Service` - User profile and conversation storage
- [ ] `AIService` - OpenAI integration and response generation
- [ ] `TTSService` - ElevenLabs text-to-speech
- [ ] `VideoService` - Video generation and script creation

### Utility Functions
- [ ] `generate_user_id()` - UUID generation
- [ ] `detect_language()` - Language detection
- [ ] `create_quiz()` - Quiz generation
- [ ] `log_api_call()` - API monitoring

---

## Success Criteria ✅

- [ ] API responds to chat messages correctly
- [ ] User profiles are stored and retrieved from Mem0
- [ ] AI responses are personalized and educational
- [ ] TTS generates audio for responses
- [ ] Video generation works for educational content
- [ ] All endpoints return proper JSON responses
- [ ] Error handling works correctly
- [ ] API is fast and responsive

---

## Risk Mitigation 🛡️

- **API Limits**: Implement rate limiting and error handling
- **Service Failures**: Have fallback responses ready
- **Memory Issues**: Optimize for production use
- **Time Constraints**: Focus on core features first
- **Integration Issues**: Test each service independently

---

## Environment Setup 🔧

### Required API Keys
```bash
# .env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
GEMINI_API_KEY=...
MEM0_API_KEY=...
```

### Development Commands
```bash
# Start development server
python main.py

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test API
curl http://localhost:8000/health
```

---

**Good luck with the backend development, Ram! 🚀**
*Remember: Keep it simple, focus on core functionality, and ship something that works!*
