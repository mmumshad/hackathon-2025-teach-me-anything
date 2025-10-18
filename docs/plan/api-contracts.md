# TechMeAnything API Contracts & Data Structures 📋

## Overview
This document defines the API contracts and data structures for the TechMeAnything educational platform.

## Base Configuration
- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **Authentication**: Frontend-generated userID passed with all requests (stored in localStorage)

---

## Data Structures 📊

### User Profile
```typescript
interface UserProfile {
  userId: string;
  userName: string;
  gradeLevel: number; // K-12
  preferences: UserPreferences;
  createdAt: string; // ISO 8601
  lastActiveAt: string; // ISO 8601
}

interface UserPreferences {
  language: Language;
  muteAudio: boolean;
  learningLevel: 'beginner' | 'intermediate' | 'advanced';
  learningStyle: 'visual' | 'auditory' | 'kinesthetic';
  preferredSubjects: string[];
}
```

### Chat Messages
```typescript
interface ChatMessage {
  id: string;
  userId: string;
  content: string;
  timestamp: string; // ISO 8601
}

interface ChatResponse {
  id: string;
  messageId: string; // References the user's message
  content: string;
  timestamp: string;
  audioUrl?: string; // Optional audio response
}

interface QuizOption {
  id: string;
  text: string;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
  correctAnswerId: string;
  explanation: string;
}
```

### Language Support
```typescript
type Language = 'en' | 'zh' | 'hi' | 'es' | 'ar';

interface LanguageInfo {
  code: Language;
  name: string;
  nativeName: string;
  voiceId: string; // ElevenLabs voice ID
}
```

---

## API Endpoints 🔌

### Chat & AI Integration

#### POST `/chat/message`
**Purpose**: Send chat message and get AI response
```typescript
// Request Headers
{
  "X-User-ID": string; // Frontend-generated userID
}

// Request Body
interface ChatRequest {
  message: ChatMessage;
  requireAudio?: boolean; // Request audio response
}

// Response
interface ChatMessageResponse {
  success: boolean;
  response: ChatResponse;
  audioUrl?: string; // Optional audio response
  videoUrl?: string; // Optional video response
  quiz?: QuizQuestion[]; // Optional array of quiz questions
}
```

---

## Authentication Flow 🔐

### Frontend Authentication
- **UserID Generation**: Frontend generates a unique userID (UUID) on first visit
- **Storage**: UserID stored in localStorage for persistence across sessions
- **Request Headers**: All API requests include `X-User-ID` header
- **Backend Identification**: Backend uses userID to identify and manage user data

### Example Frontend Implementation
```typescript
// Generate and store userID
const userId = localStorage.getItem('userId') || generateUUID();
localStorage.setItem('userId', userId);

// Include in all API requests
const headers = {
  'Content-Type': 'application/json',
  'X-User-ID': userId
};
```

### Backend User Management
- **Auto-Creation**: Backend automatically creates user profile on first API call
- **Auto-Management**: User profiles managed entirely by backend based on chat interactions
- **Data Storage**: User data stored in Mem0 using userID as key
- **No Profile Endpoints**: Frontend doesn't need to manage user profiles directly
- **No Login Required**: Users can start chatting immediately

---

## Error Handling 🚨

### Standard Error Response
```typescript
interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
  };
}
```

### Error Codes
- `USER_NOT_FOUND`: User ID doesn't exist
- `INVALID_LANGUAGE`: Unsupported language code
- `AUDIO_PROCESSING_FAILED`: TTS/STT service error
- `VIDEO_GENERATION_FAILED`: Video creation error
- `INVALID_REQUEST`: Malformed request data
- `SERVICE_UNAVAILABLE`: External service down

---

## Environment Variables 🔧
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GEMINI_API_KEY=your_gemini_api_key
MEM0_API_KEY=your_mem0_api_key

# Optional Configuration
MAX_VIDEO_DURATION=60
DEFAULT_LANGUAGE=en
RATE_LIMIT_ENABLED=true
```

---

## Testing Endpoints 🧪

### Health Check
#### GET `/health`
```typescript
// Response
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    openai: 'up' | 'down';
    elevenlabs: 'up' | 'down';
    mem0: 'up' | 'down';
    gemini: 'up' | 'down';
  };
  timestamp: string;
}
```

---

*This API contract supports the 24-hour hackathon timeline with focus on core MVP features! 🎯*
