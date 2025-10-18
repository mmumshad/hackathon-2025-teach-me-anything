
# TechMeAnything 🎓

> AI-powered educational platform for K12 students with personalized learning through text/voice chat and video generation.

## 🌟 Overview

TechMeAnything is an intelligent tutoring system designed for K12 students that combines AI-powered conversations, multimedia content generation, and personalized learning experiences. The platform uses advanced AI services to create engaging educational content tailored to each student's needs.

### Key Features ✨

- **🤖 AI-Powered Chat**: Intelligent conversations with personalized responses
- **🎤 Voice Integration**: Text-to-speech narration and voice input
- **🎬 Video Generation**: Educational videos created on-demand
- **🧠 Interactive Quizzes**: Knowledge assessment with instant feedback
- **🌍 Multilingual Support**: English, Chinese, Hindi, Spanish, Arabic
- **👤 User Profiling**: Automatic assessment and personalization
- **📱 Responsive Design**: Works seamlessly on desktop and mobile

## 🛠️ Tech Stack

### Frontend
- **Next.js** - React framework
- **shadcn/ui** - Modern UI components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling

### Backend
- **FastAPI** - High-performance Python API
- **Python** - Core backend language

### AI Services
- **OpenAI** - Large Language Model (GPT-4)
- **ElevenLabs** - Text-to-Speech
- **Gemini/Sora 2** - Video Generation
- **Mem0** - AI-native data storage

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- API keys for AI services

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackathon-2025-teach-me-anything
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `backend/.env` with your API keys:
```bash
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GEMINI_API_KEY=your_gemini_api_key
MEM0_API_KEY=your_mem0_api_key
```

### 4. Start Backend Server
```bash
cd backend
python main.py
```
Backend will be available at `http://localhost:8000`

### 5. Frontend Setup
```bash
cd frontend
npm install
```

### 6. Start Frontend Development Server
```bash
cd frontend
npm run dev
```
Frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
hackathon-2025-teach-me-anything/
├── docs/
│   └── plan/
│       ├── high-level-plan.md      # Overall project strategy
│       ├── api-contracts.md        # API specifications
│       ├── frontend-plan.md        # Frontend development plan
│       └── backend-plan.md         # Backend development plan
├── backend/
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables
├── frontend/
│   ├── src/                        # Next.js source code
│   ├── package.json                # Node.js dependencies
│   └── .env.local                  # Frontend environment
└── README.md                       # This file
```

## 🎯 How It Works

### User Experience Flow
1. **First Visit**: User enters name and grade level
2. **Chat Interface**: Clean, minimal chat UI with text/voice input
3. **AI Interaction**: Personalized responses based on user profile
4. **Multimedia Content**: Audio narration and educational videos
5. **Knowledge Assessment**: Interactive quizzes for learning validation

### Technical Flow
1. **Frontend**: Generates userID, stores in localStorage
2. **API Communication**: Sends chat messages with userID header
3. **Backend Processing**: 
   - Retrieves user profile from Mem0
   - Generates AI response with OpenAI
   - Creates audio with ElevenLabs (if requested)
   - Generates video content (if educational)
   - Creates quiz questions for assessment
4. **Response**: Returns text, audio, video, and quiz data

## 🔧 API Endpoints

### Main Endpoint
- `POST /api/v1/chat/message` - Send chat message and receive AI response

### Health Check
- `GET /health` - API health status

## 🧪 Testing

### Backend Testing
```bash
# Health check
curl http://localhost:8000/health

# Chat message
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

### Frontend Testing
- Open `http://localhost:3000`
- Enter user information
- Start chatting with the AI
- Test voice input/output
- Try educational topics to see video generation

## 📋 Development Plans

Detailed development plans are available in the `docs/plan/` directory:
- **Frontend Plan**: Step-by-step Next.js development guide
- **Backend Plan**: FastAPI implementation roadmap
- **API Contracts**: Complete API specifications

## 🎨 UI/UX Design

### Design Principles
- **Minimal**: Clean white background, focused on content
- **Accessible**: Easy to use for K12 students
- **Responsive**: Works on all device sizes
- **Intuitive**: Simple navigation and clear interactions

### Key UI Elements
- **Mute Toggle**: Top-left corner for audio control
- **Settings Menu**: Top-right corner (3 dots) for user options
- **Chat Interface**: Central conversation area
- **Voice Input**: Microphone button for speech input

## 🌍 Multilingual Support

Supported languages:
- English (en)
- Chinese (zh)
- Hindi (hi)
- Spanish (es)
- Arabic (ar)

Language detection is automatic based on user input.

## 🚧 Development Status

This project is currently in active development for a 24-hour hackathon. The MVP focuses on core features:

- ✅ Basic chat interface
- ✅ AI-powered responses
- ✅ User authentication
- ✅ Audio narration
- ✅ Video generation
- ✅ Quiz functionality
- ✅ Multilingual support

## 🤝 Contributing

This is a hackathon project. For development questions or issues, please refer to the detailed plans in the `docs/plan/` directory.

## 📄 License

This project is part of a hackathon submission. Please refer to the LICENSE file for details.

---

**Built with ❤️ for K12 education**





