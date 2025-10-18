# Frontend Development Plan - TechMeAnything 🎨

## Developer: Mumshad
## Timeline: 24-Hour Hackathon Sprint
## Tech Stack: Next.js + shadcn/ui + TypeScript

---

## Phase 1: Project Setup (Hours 1-3) ⚙️

### Hour 1: Next.js Initialization
- [ ] **Initialize Next.js project**
  ```bash
  npx create-next-app@latest frontend --typescript --tailwind --eslint --app
  cd frontend
  ```
- [ ] **Install shadcn/ui**
  ```bash
  npx shadcn-ui@latest init
  npx shadcn-ui@latest add button input textarea card
  ```
- [ ] **Install additional dependencies**
  ```bash
  npm install uuid @types/uuid
  npm install lucide-react
  ```

### Hour 2: Project Structure Setup
- [ ] **Create folder structure**
  ```
  src/
  ├── app/
  ├── components/
  │   ├── ui/           # shadcn components
  │   ├── chat/         # Chat components
  │   ├── auth/         # Auth components
  │   └── layout/       # Layout components
  ├── lib/
  │   ├── api.ts        # API calls
  │   ├── utils.ts      # Utility functions
  │   └── types.ts      # TypeScript types
  └── hooks/            # Custom hooks
  ```
- [ ] **Set up environment variables**
  ```bash
  # .env.local
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  ```

### Hour 3: Basic Layout & Styling
- [ ] **Create main layout component**
  - Clean white background
  - Header with mute toggle (top-left)
  - Settings dropdown (top-right, 3 dots)
  - Main chat area
- [ ] **Set up global styles**
  - Clean, minimal design
  - Mobile-responsive
  - Dark mode support (optional)

---

## Phase 2: Authentication & User Management (Hours 4-6) 🔐

### Hour 4: UserID Generation & Storage
- [ ] **Create userID utility functions**
  ```typescript
  // lib/utils.ts
  export const generateUserId = () => crypto.randomUUID();
  export const getStoredUserId = () => localStorage.getItem('userId');
  export const storeUserId = (id: string) => localStorage.setItem('userId', id);
  ```
- [ ] **Create userID collection component**
  - Simple form with name input
  - Grade level selection (K-12)
  - Generate and store userID
  - Redirect to chat after setup

### Hour 5: Settings & User Management
- [ ] **Create settings dropdown component**
  - Display current userID
  - Sign out option (clear localStorage)
  - Mute/unmute toggle
- [ ] **Implement mute toggle functionality**
  - Store preference in localStorage
  - Visual indicator (speaker icon)
  - Default to muted

### Hour 6: API Integration Setup
- [ ] **Create API client**
  ```typescript
  // lib/api.ts
  const API_BASE = process.env.NEXT_PUBLIC_API_URL;
  
  export const apiClient = {
    chat: async (message: ChatMessage, requireAudio?: boolean) => {
      const userId = getStoredUserId();
      return fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify({ message, requireAudio })
      });
    }
  };
  ```

---

## Phase 3: Chat Interface (Hours 7-9) 💬

### Hour 7: Chat UI Components
- [ ] **Create chat message components**
  - User message bubble (right-aligned)
  - AI response bubble (left-aligned)
  - Timestamp display
  - Message status indicators
- [ ] **Create chat input component**
  - Text input with send button
  - Voice input button (microphone icon)
  - Auto-resize textarea
  - Enter to send functionality

### Hour 8: Message Display System
- [ ] **Implement message list component**
  - Scrollable message container
  - Auto-scroll to bottom on new messages
  - Message loading states
  - Error message display
- [ ] **Create message types**
  ```typescript
  // lib/types.ts
  interface ChatMessage {
    id: string;
    userId: string;
    content: string;
    timestamp: string;
  }
  
  interface ChatResponse {
    id: string;
    messageId: string;
    content: string;
    timestamp: string;
    audioUrl?: string;
  }
  ```

### Hour 9: Chat State Management
- [ ] **Implement chat state**
  - Message history
  - Loading states
  - Error handling
  - Connection status
- [ ] **Connect to backend API**
  - Send messages to `/api/v1/chat/message`
  - Handle responses
  - Display AI responses
  - Error handling

---

## Phase 4: Voice Integration (Hours 10-12) 🎤

### Hour 10: Voice Input Implementation
- [ ] **Add voice input capability**
  ```typescript
  // hooks/useVoiceInput.ts
  const useVoiceInput = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    
    const startRecording = () => {
      // Browser Speech Recognition API
    };
    
    const stopRecording = () => {
      // Stop recording and get transcript
    };
    
    return { isRecording, transcript, startRecording, stopRecording };
  };
  ```
- [ ] **Create voice input button**
  - Microphone icon
  - Recording state indicator
  - Click to start/stop recording

### Hour 11: Audio Playback
- [ ] **Implement audio playback**
  ```typescript
  // components/chat/AudioPlayer.tsx
  const AudioPlayer = ({ audioUrl, isMuted }: { audioUrl: string, isMuted: boolean }) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    
    const playAudio = () => {
      if (!isMuted && audioRef.current) {
        audioRef.current.play();
      }
    };
    
    return <audio ref={audioRef} src={audioUrl} onLoadedData={playAudio} />;
  };
  ```
- [ ] **Add audio controls**
  - Play/pause button
  - Volume control
  - Respect mute setting

### Hour 12: Voice UI Integration
- [ ] **Integrate voice with chat**
  - Voice input → text message
  - Audio response playback
  - Visual feedback for audio states
- [ ] **Test voice functionality**
  - Browser compatibility
  - Error handling
  - Fallback to text-only

---

## Phase 5: Quiz Integration (Hours 13-15) 🧠

### Hour 13: Quiz Components
- [ ] **Create quiz question component**
  ```typescript
  // components/chat/QuizQuestion.tsx
  interface QuizQuestionProps {
    question: QuizQuestion;
    onAnswer: (answerId: string) => void;
  }
  
  const QuizQuestion = ({ question, onAnswer }: QuizQuestionProps) => {
    return (
      <div className="quiz-container">
        <h3>{question.question}</h3>
        <div className="options">
          {question.options.map(option => (
            <button key={option.id} onClick={() => onAnswer(option.id)}>
              {option.text}
            </button>
          ))}
        </div>
      </div>
    );
  };
  ```

### Hour 14: Quiz Logic & Feedback
- [ ] **Implement quiz logic**
  - Answer selection
  - Correct/incorrect feedback
  - Explanation display
  - Score tracking
- [ ] **Create quiz feedback component**
  - Correct answer highlighting
  - Explanation text
  - Next question button
  - Quiz completion summary

### Hour 15: Quiz Integration with Chat
- [ ] **Integrate quiz with chat flow**
  - Display quiz after AI response
  - Handle quiz completion
  - Continue conversation flow
- [ ] **Test quiz functionality**
  - Multiple question handling
  - Answer validation
  - User experience flow

---

## Phase 6: Video Integration (Hours 16-18) 🎬

### Hour 16: Video Display Component
- [ ] **Create video player component**
  ```typescript
  // components/chat/VideoPlayer.tsx
  const VideoPlayer = ({ videoUrl }: { videoUrl: string }) => {
    return (
      <div className="video-container">
        <video controls width="100%" height="auto">
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    );
  };
  ```
- [ ] **Add video loading states**
  - Loading spinner
  - Error handling
  - Fallback content

### Hour 17: Video Generation Integration
- [ ] **Add video generation trigger**
  - Detect when AI response includes video
  - Display video player
  - Handle video loading
- [ ] **Implement video + audio sync**
  - Play video and audio together
  - Respect mute settings
  - Volume controls

### Hour 18: Video UI Polish
- [ ] **Polish video experience**
  - Responsive video sizing
  - Fullscreen support
  - Video controls
  - Error handling
- [ ] **Test video functionality**
  - Different video formats
  - Mobile compatibility
  - Performance optimization

---

## Phase 7: Testing & Polish (Hours 19-24) 🧪

### Hours 19-20: Integration Testing
- [ ] **End-to-end testing**
  - Complete user flow
  - All features working together
  - Cross-browser testing
- [ ] **Bug fixes**
  - Fix critical issues
  - Performance optimization
  - Error handling improvements

### Hours 21-22: UI/UX Polish
- [ ] **Visual refinements**
  - Consistent spacing
  - Better typography
  - Smooth animations
  - Loading states
- [ ] **Mobile optimization**
  - Touch-friendly interface
  - Responsive design
  - Mobile-specific features

### Hours 23-24: Final Testing & Demo Prep
- [ ] **Final testing**
  - All features working
  - Performance check
  - Error scenarios
- [ ] **Demo preparation**
  - Create demo script
  - Prepare test scenarios
  - Document key features

---

## Key Components to Build 🧩

### Core Components
- [ ] `UserSetup` - Initial user registration
- [ ] `ChatInterface` - Main chat UI
- [ ] `MessageBubble` - Individual message display
- [ ] `ChatInput` - Text and voice input
- [ ] `AudioPlayer` - Audio playback
- [ ] `VideoPlayer` - Video display
- [ ] `QuizQuestion` - Quiz interface
- [ ] `SettingsDropdown` - User settings

### Utility Functions
- [ ] `generateUserId()` - UUID generation
- [ ] `getStoredUserId()` - localStorage retrieval
- [ ] `apiClient.chat()` - API communication
- [ ] `useVoiceInput()` - Voice input hook
- [ ] `useChat()` - Chat state management

---

## Success Criteria ✅

- [ ] User can create account and start chatting
- [ ] Chat interface is clean and intuitive
- [ ] Voice input/output works smoothly
- [ ] Quiz functionality is engaging
- [ ] Video playback works correctly
- [ ] Application is mobile-responsive
- [ ] All features work together seamlessly

---

## Risk Mitigation 🛡️

- **Browser Compatibility**: Test on Chrome, Firefox, Safari
- **Voice API Issues**: Have text fallback ready
- **Performance**: Optimize for mobile devices
- **Time Constraints**: Focus on core features first
- **API Integration**: Test with mock data first

---

**Good luck with the frontend development, Mumshad! 🚀**
*Remember: Keep it simple, focus on user experience, and ship something that works!*
