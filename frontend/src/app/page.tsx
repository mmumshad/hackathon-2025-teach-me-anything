'use client';

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { generateUUID, getStoredUserId, storeUserId } from '@/lib/utils';
import ApiClient, { type ChatMessage, type ChatResponse } from '@/lib/api';
import { Particles } from '@/components/ui/particles';
import { Quiz } from '@/components/ui/quiz';
import LoaderOne from '@/components/ui/loader-one';
import { VideoGenerationProgress } from '@/components/ui/video-generation-progress';
import { AudiobookUploadCard } from '@/components/ui/audiobook-upload-card';
import { AudiobookPlayer } from '@/components/ui/audiobook-player';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingText, setTypingText] = useState('');
  const [typingDisplay, setTypingDisplay] = useState(''); // Separate state for typing animation
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [skipTyping, setSkipTyping] = useState(false);
  const [currentVideoUrl, setCurrentVideoUrl] = useState<string | null>(null);
  const [currentVideoId, setCurrentVideoId] = useState<string | null>(null);
  const [isVideoGenerating, setIsVideoGenerating] = useState(false);
  const [currentResponseType, setCurrentResponseType] = useState<'video' | 'quiz' | 'text' | 'audiobook' | null>(null);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [currentQuiz, setCurrentQuiz] = useState<ChatResponse['quiz']>(undefined);
  const [userId, setUserId] = useState<string>('');
  const [apiClient, setApiClient] = useState<ApiClient | null>(null);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [showAudiobookUpload, setShowAudiobookUpload] = useState(false);
  const [isAudiobookGenerating, setIsAudiobookGenerating] = useState(false);
  const [currentAudiobook, setCurrentAudiobook] = useState<{
    chunks: string[];
    info: any;
  } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Generate or retrieve user ID
  useEffect(() => {
    const storedUserId = getStoredUserId();
    if (storedUserId) {
      setUserId(storedUserId);
      setApiClient(new ApiClient(storedUserId));
    } else {
      const newUserId = generateUUID();
      storeUserId(newUserId);
      setUserId(newUserId);
      setApiClient(new ApiClient(newUserId));
    }
  }, []);

  // Typing animation effect
  useEffect(() => {
    if (isTyping && typingText && !skipTyping) {
      let currentIndex = 0;
      const interval = setInterval(() => {
        // Check if skipTyping was triggered during animation
        if (skipTyping) {
          clearInterval(interval);
          return;
        }
        
        if (currentIndex < typingText.length) {
          setTypingDisplay(typingText.substring(0, currentIndex + 1)); // Use separate state
          currentIndex++;
        } else {
          clearInterval(interval);
          // Start transition immediately
          setIsTransitioning(true);
          setIsTyping(false);
          
          // Move message up and change to small text after typing completes
          setTimeout(() => {
            // Always add to message history - messages should persist
            setMessages(prev => [...prev, {
              id: generateUUID(),
              userId: userId,
              content: typingText,
              timestamp: new Date().toISOString()
            }]);
            setCurrentMessage('');
            setTypingText('');
            // Keep video and audio URLs - don't clear them
            setIsWaitingForResponse(false);
            setIsTransitioning(false);
          }, 1000);
        }
      }, 50); // Typing speed

      return () => clearInterval(interval);
    }
  }, [isTyping, typingText, skipTyping]);

  // Skip typing animation effect
  useEffect(() => {
    if (skipTyping && isTyping && typingText) {
      // Immediately show full text and complete the animation
      setTypingDisplay(typingText);
      setIsTyping(false);
      setIsTransitioning(true);
      
      // Shorter delay for immediate response
      setTimeout(() => {
        // Always add to message history - messages should persist
        setMessages(prev => [...prev, {
          id: generateUUID(),
          userId: userId,
          content: typingText,
          timestamp: new Date().toISOString()
        }]);
        setCurrentMessage('');
        setTypingText('');
        setIsWaitingForResponse(false);
        setIsTransitioning(false);
        setSkipTyping(false); // Reset skip state
      }, 500); // Reduced from 1000ms to 500ms for faster response
    }
  }, [skipTyping, isTyping, typingText, userId]);

  // Global key listener for Enter key (works even when input is disabled)
  useEffect(() => {
    const handleGlobalKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        // If currently typing, skip the animation
        if (isTyping) {
          e.preventDefault();
          setSkipTyping(true);
          return;
        }
      }
    };

    // Add global event listener
    document.addEventListener('keydown', handleGlobalKeyPress);

    return () => {
      document.removeEventListener('keydown', handleGlobalKeyPress);
    };
  }, [isTyping, skipTyping, typingText]);

  // Auto-focus input when not typing
  useEffect(() => {
    if (!isTyping && !isWaitingForResponse && !isTransitioning && !isVideoGenerating && inputRef.current) {
      // Small delay to ensure DOM is ready
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isTyping, isWaitingForResponse, isTransitioning]);

  // Video polling effect
  useEffect(() => {
    if (!currentVideoId || !apiClient || !isVideoGenerating) return;

    const pollVideoStatus = async () => {
      try {
        const statusResponse = await apiClient.checkVideoStatus(currentVideoId);
        const videoStatus = statusResponse.video;

        if (videoStatus.status === 'completed') {
          // Video is ready, get the video URL
          const videoUrl = apiClient.getVideoUrl(currentVideoId);
          console.log('🎬 DEBUG: Video generation completed, setting URL:', videoUrl);
          console.log('🎬 DEBUG: Current quiz state when video completes:', !!currentQuiz);
          
          // Only set video URL if current response type is video
          if (currentResponseType === 'video') {
            console.log('🎬 DEBUG: Current response type is video - setting video URL');
            setCurrentVideoUrl(videoUrl);
          } else {
            console.log('🎬 DEBUG: Current response type is', currentResponseType, '- NOT setting video URL');
          }
          
          setIsVideoGenerating(false);
          setCurrentVideoId(null);
        } else if (videoStatus.status === 'failed') {
          // Video generation failed
          console.error('Video generation failed:', videoStatus.error);
          setIsVideoGenerating(false);
          setCurrentVideoId(null);
        } else {
          // Still generating, poll again in 7 seconds
          setTimeout(pollVideoStatus, 7000);
        }
      } catch (error) {
        console.error('Error polling video status:', error);
        // Retry in 5 seconds on error
        setTimeout(pollVideoStatus, 5000);
      }
    };

    // Start polling
    pollVideoStatus();
  }, [currentVideoId, apiClient, isVideoGenerating]);

  const sendMessage = async () => {
    console.log('🚀 DEBUG: sendMessage called');
    console.log('🚀 DEBUG: Current state before send:', { currentVideoUrl, currentVideoId, isVideoGenerating, isWaitingForResponse, currentMessage: currentMessage.trim() });
    
    if (!currentMessage.trim() || isWaitingForResponse || !apiClient) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    // Clear previous video/audio/quiz when sending new message
    console.log('🚀 DEBUG: Clearing video state at start of sendMessage');
    setCurrentVideoUrl(null);
    setCurrentVideoId(null);
    setIsVideoGenerating(false);
    setCurrentAudioUrl(null);
    setCurrentQuiz(undefined);
    setCurrentResponseType(null); // Reset response type when sending new message
    setSkipTyping(false); // Reset skip state
    setIsWaitingForResponse(true);

    try {
      const message: ChatMessage = {
        id: generateUUID(),
        userId: userId,
        content: userMessage,
        timestamp: new Date().toISOString()
      };

      const data = await apiClient.sendMessage(message, isAudioEnabled);
      
      // Debug: Print the complete data received from backend
      console.log('📡 DEBUG: Backend response data:', {
        hasVideo: !!(data.video && data.video.videoId),
        videoId: data.video?.videoId,
        hasQuiz: !!(data.quiz && data.quiz.length > 0),
        quizLength: data.quiz?.length,
        hasAudiobook: !!(data.audiobookChunks && data.audiobookChunks.length > 0),
        audiobookChunksLength: data.audiobookChunks?.length,
        hasAudio: !!data.audioUrl,
        responseContent: data.response?.content?.substring(0, 100) + '...',
        fullData: data
      });
      
      // Start typing animation for the response
      setTypingText(data.response.content);
      
      // Determine response type and handle accordingly
      let responseType: 'video' | 'quiz' | 'text' | 'audiobook' = 'text';
      
      if (data.video && data.video.videoId) {
        responseType = 'video';
        console.log('🎬 DEBUG: Video response detected:', data.video.videoId);
        setCurrentVideoId(data.video.videoId);
        setIsVideoGenerating(true);
        // Don't set videoUrl yet - will be set when polling completes
      } else if (data.quiz && data.quiz.length > 0) {
        responseType = 'quiz';
        console.log('🧩 DEBUG: Quiz response detected');
      } else if (data.audiobookChunks && data.audiobookChunks.length > 0) {
        responseType = 'audiobook';
        console.log('🎵 DEBUG: Audiobook response detected');
      } else {
        console.log('📝 DEBUG: Text response detected');
      }
      
      // Set the current response type
      setCurrentResponseType(responseType);
      
      // Clear video state if not a video response
      if (responseType !== 'video') {
        console.log('🎬 DEBUG: Not a video response - clearing video state');
        setCurrentVideoUrl(null);
        setCurrentVideoId(null);
        setIsVideoGenerating(false);
      }
      
      setCurrentAudioUrl(data.audioUrl || null);
      
      // Debug quiz handling
      console.log('🧩 DEBUG: Quiz data received:', data.quiz);
      const quizToSet = data.quiz && data.quiz.length > 0 ? data.quiz : undefined;
      console.log('🧩 DEBUG: Setting quiz to:', quizToSet);
      setCurrentQuiz(quizToSet);
      setIsWaitingForResponse(false); // Stop waiting, start typing
      setIsTyping(true);
    } catch (error) {
      console.error('Error sending message:', error);
      setTypingText('Sorry, I encountered an error. Please try again.');
      setIsWaitingForResponse(false); // Stop waiting, start typing error message
      setIsTyping(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      
      // If currently typing, skip the animation
      if (isTyping) {
        setSkipTyping(true);
        return;
      }
      
      // Otherwise, send the message normally
      sendMessage();
    }
  };

  const handlePageClick = () => {
    // Focus input when clicking anywhere on the page
    if (inputRef.current && !isTyping && !isTransitioning && !isWaitingForResponse && !isVideoGenerating && !(currentQuiz && currentQuiz.length > 0)) {
      inputRef.current.focus();
    }
  };

  const clearQuiz = () => {
    console.log('🧩 DEBUG: clearQuiz called - current state:', { currentVideoUrl, currentVideoId, isVideoGenerating, currentResponseType });
    setCurrentQuiz(undefined);
    setCurrentResponseType(null); // Reset response type when quiz is completed
    // Clear video state when quiz is completed
    console.log('🧩 DEBUG: Clearing video state in clearQuiz');
    setCurrentVideoUrl(null);
    setCurrentVideoId(null);
    setIsVideoGenerating(false);
    setCurrentAudioUrl(null);
    // Don't remove messages from history - keep them visible
    // Focus input after quiz completion
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 100);
  };

  const handleAudiobookUpload = async (file: File) => {
    if (!apiClient) return;

    // Clear video state when starting audiobook generation
    setCurrentVideoUrl(null);
    setCurrentVideoId(null);
    setIsVideoGenerating(false);
    setCurrentAudioUrl(null);
    setCurrentQuiz(undefined);
    setCurrentResponseType(null); // Reset response type when starting audiobook

    setIsAudiobookGenerating(true);
    // Don't hide the upload card - keep it visible to show progress

    try {
      // Create a form data to send the file
      const formData = new FormData();
      formData.append('message', 'Please help me understand this document');
      formData.append('message_id', generateUUID());
      formData.append('user_id', userId);
      formData.append('timestamp', new Date().toISOString());
      formData.append('require_audio', 'false'); // This will be converted to boolean by FastAPI
      formData.append('attached_file', file);

      const response = await fetch('http://localhost:8000/api/v1/chat/message', {
        method: 'POST',
        headers: {
          'X-User-ID': userId,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate audiobook: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      const responseData = data.responses[0];

      if (responseData.audiobookChunks && responseData.audiobookInfo) {
        setCurrentAudiobook({
          chunks: responseData.audiobookChunks,
          info: responseData.audiobookInfo
        });
        // Hide upload card and show player
        setShowAudiobookUpload(false);
      } else {
        throw new Error('No audiobook data received');
      }
    } catch (error) {
      console.error('Error generating audiobook:', error);
      alert(`Failed to generate audiobook: ${error instanceof Error ? error.message : 'Unknown error'}`);
      // Hide upload card on error
      setShowAudiobookUpload(false);
    } finally {
      setIsAudiobookGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col relative" onClick={handlePageClick}>
      {/* Audio Controls - Top Right Corner */}
      <div className="fixed top-4 right-4 z-50 flex gap-2">
        {/* Audiobook Button */}
        <button
          onClick={() => setShowAudiobookUpload(!showAudiobookUpload)}
          disabled={isTyping || isTransitioning || isWaitingForResponse || isVideoGenerating || isAudiobookGenerating || (currentQuiz && currentQuiz.length > 0)}
          className={`p-3 rounded-full transition-all duration-200 shadow-lg ${
            showAudiobookUpload 
              ? 'bg-purple-500 text-white hover:bg-purple-600' 
              : 'bg-gray-200 text-gray-500 hover:bg-gray-300'
          } ${isTyping || isTransitioning || isWaitingForResponse || isVideoGenerating || isAudiobookGenerating || (currentQuiz && currentQuiz.length > 0) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          title="Create Audiobook from PDF"
        >
          {/* Audiobook icon (book with sound waves) */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
            <path d="M12 14c1.66 0 3-1.34 3-3V7h2v4c0 2.76-2.24 5-5 5s-5-2.24-5-5V7h2v4c0 1.66 1.34 3 3 3z" opacity="0.6"/>
          </svg>
        </button>

        {/* Audio Toggle Button */}
        <button
          onClick={() => setIsAudioEnabled(!isAudioEnabled)}
          disabled={isTyping || isTransitioning || isWaitingForResponse || isVideoGenerating || isAudiobookGenerating || (currentQuiz && currentQuiz.length > 0)}
          className={`p-3 rounded-full transition-all duration-200 shadow-lg ${
            isAudioEnabled 
              ? 'bg-blue-500 text-white hover:bg-blue-600' 
              : 'bg-gray-200 text-gray-500 hover:bg-gray-300'
          } ${isTyping || isTransitioning || isWaitingForResponse || isVideoGenerating || isAudiobookGenerating || (currentQuiz && currentQuiz.length > 0) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          title={isAudioEnabled ? 'Audio enabled - Click to disable' : 'Audio disabled - Click to enable'}
        >
          {isAudioEnabled ? (
            // Audio enabled icon (speaker with sound waves)
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          ) : (
            // Audio disabled icon (speaker muted)
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
            </svg>
          )}
        </button>
      </div>

      {/* Particles Background */}
      <Particles
        className="absolute inset-0 z-0"
        quantity={50}
        color="#3b82f6"
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 relative z-10">
        {/* Messages History - Show only last 2 messages */}
        {messages.length > 0 && (
          <div className="w-full max-w-4xl mb-8 space-y-6">
            {messages.slice(-2).map((message, index) => {
              const isOldest = messages.length > 1 && index === 0;
              return (
                <div 
                  key={message.id} 
                  className={`text-lg text-gray-600 text-center leading-relaxed ${
                    isOldest ? 'relative' : ''
                  }`}
                  style={isOldest ? {
                    background: 'linear-gradient(to bottom, transparent 0%, rgba(107, 114, 128, 0.1) 20%, rgba(107, 114, 128, 0.2) 40%, rgba(107, 114, 128, 0.3) 60%, rgba(107, 114, 128, 0.4) 80%, rgba(107, 114, 128, 0.5) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    color: 'transparent'
                  } : {}}
                >
                  {message.content}
                </div>
              );
            })}
          </div>
        )}

        {/* Current Typing Message */}
        {(isTyping || isTransitioning) && (
          <div className="text-center mb-8">
            <div className={`font-light leading-relaxed max-w-5xl mx-auto transition-all duration-1000 ease-in-out ${
              isTyping 
                ? (currentVideoUrl ? 'text-3xl text-gray-800' : 'text-5xl text-gray-800')
                : 'text-lg text-gray-600'
            }`}>
              {isTyping ? typingDisplay : typingText}
              {isTyping && <span className="animate-pulse text-gray-500">|</span>}
            </div>
            {/* Skip hint */}
            {isTyping && (
              <div className="text-xs text-gray-400 mt-2 opacity-70">
                Press Enter to skip animation
              </div>
            )}
          </div>
        )}

        {/* Loading Spinner - Show while waiting for backend response */}
        {isWaitingForResponse && !currentQuiz && (
          <div className="text-center mb-8">
            <LoaderOne />
          </div>
        )}

        {/* Persistent Video Player */}
        {(currentVideoUrl || isVideoGenerating) && currentResponseType === 'video' && (
          <div className="mb-8 max-w-7xl mx-auto">
            <div className="relative w-full" style={{ aspectRatio: '16/9', minHeight: '500px' }}>
              {currentVideoUrl ? (
                // Video is ready - show actual video
                <video 
                  src={currentVideoUrl} 
                  autoPlay 
                  loop
                  playsInline
                  controls
                  className="absolute inset-0 w-full h-full object-cover rounded-[2rem] shadow-2xl"
                >
                  Your browser does not support the video tag.
                </video>
              ) : (
                // Video is generating - show placeholder with progress bar
                <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-blue-50 to-purple-50 rounded-[2rem] shadow-2xl flex items-center justify-center">
                  <VideoGenerationProgress isGenerating={isVideoGenerating} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Persistent Audio Player */}
        {currentAudioUrl && (
          <div className="mb-4 max-w-2xl mx-auto">
            <audio 
              src={currentAudioUrl} 
              controls 
              autoPlay
              className="w-full"
            >
              Your browser does not support the audio tag.
            </audio>
          </div>
        )}

        {/* Quiz Interface */}
        {currentQuiz && <Quiz quiz={currentQuiz} onQuizComplete={clearQuiz} />}

        {/* Audiobook Upload Card */}
        <AudiobookUploadCard
          isVisible={showAudiobookUpload}
          isGenerating={isAudiobookGenerating}
          onFileUpload={handleAudiobookUpload}
          onClose={() => setShowAudiobookUpload(false)}
        />

        {/* Audiobook Player */}
        {currentAudiobook && (
          <AudiobookPlayer
            audiobookChunks={currentAudiobook.chunks}
            audiobookInfo={currentAudiobook.info}
            onClose={() => setCurrentAudiobook(null)}
          />
        )}

        {/* Input Field - Always visible but disabled during animations */}
        <div className="w-full max-w-5xl">
          <Input
            ref={inputRef}
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder=""
            className="text-center text-4xl font-light border-none shadow-none focus:ring-0 focus:border-none bg-transparent py-12 px-6"
            disabled={isTyping || isTransitioning || isWaitingForResponse || isVideoGenerating || (currentQuiz && currentQuiz.length > 0)}
            style={{ fontSize: '2.5rem', lineHeight: '1.4' }}
          />
        </div>

        {/* Send Button (hidden, Enter key triggers send) */}
        <Button
          onClick={sendMessage}
          disabled={!currentMessage.trim() || isWaitingForResponse}
          className="sr-only"
        >
          Send
        </Button>
      </div>
    </div>
  );
}