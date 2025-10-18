'use client';

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { generateUUID, getStoredUserId, storeUserId } from '@/lib/utils';
import ApiClient, { type ChatMessage, type ChatResponse } from '@/lib/api';
import { Particles } from '@/components/ui/particles';
import { Quiz } from '@/components/ui/quiz';
import LoaderOne from '@/components/ui/loader-one';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingText, setTypingText] = useState('');
  const [typingDisplay, setTypingDisplay] = useState(''); // Separate state for typing animation
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [currentVideoUrl, setCurrentVideoUrl] = useState<string | null>(null);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [currentQuiz, setCurrentQuiz] = useState<ChatResponse['quiz']>(undefined);
  const [userId, setUserId] = useState<string>('');
  const [apiClient, setApiClient] = useState<ApiClient | null>(null);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
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
    if (isTyping && typingText) {
      let currentIndex = 0;
      const interval = setInterval(() => {
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
            // Only add to message history if there's no quiz
            if (!currentQuiz) {
              setMessages(prev => [...prev, {
                id: generateUUID(),
                userId: userId,
                content: typingText,
                timestamp: new Date().toISOString()
              }]);
            }
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
  }, [isTyping, typingText]);

  // Auto-focus input when not typing
  useEffect(() => {
    if (!isTyping && !isWaitingForResponse && !isTransitioning && inputRef.current) {
      // Small delay to ensure DOM is ready
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isTyping, isWaitingForResponse, isTransitioning]);

  const sendMessage = async () => {
    if (!currentMessage.trim() || isWaitingForResponse || !apiClient) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    // Clear previous video/audio/quiz when sending new message
    setCurrentVideoUrl(null);
    setCurrentAudioUrl(null);
    setCurrentQuiz(undefined);
    setIsWaitingForResponse(true);

    try {
      const message: ChatMessage = {
        id: generateUUID(),
        userId: userId,
        content: userMessage,
        timestamp: new Date().toISOString()
      };

      const data = await apiClient.sendMessage(message, isAudioEnabled);
      // Start typing animation for the response
      setTypingText(data.response.content);
      setCurrentVideoUrl(data.videoUrl || null);
      setCurrentAudioUrl(data.audioUrl || null);
      setCurrentQuiz(data.quiz);
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
      sendMessage();
    }
  };

  const handlePageClick = () => {
    // Focus input when clicking anywhere on the page
    if (inputRef.current && !isTyping && !isTransitioning && !isWaitingForResponse && !currentQuiz) {
      inputRef.current.focus();
    }
  };

  const clearQuiz = () => {
    setCurrentQuiz(undefined);
    // Remove the last message from history if it was added during quiz
    setMessages(prev => prev.slice(0, -1));
    // Focus input after quiz completion
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 100);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col relative" onClick={handlePageClick}>
      {/* Audio Toggle Button - Top Right Corner */}
      <button
        onClick={() => setIsAudioEnabled(!isAudioEnabled)}
        disabled={isTyping || isTransitioning || isWaitingForResponse || !!currentQuiz}
        className={`fixed top-4 right-4 z-50 p-3 rounded-full transition-all duration-200 shadow-lg ${
          isAudioEnabled 
            ? 'bg-blue-500 text-white hover:bg-blue-600' 
            : 'bg-gray-200 text-gray-500 hover:bg-gray-300'
        } ${isTyping || isTransitioning || isWaitingForResponse || !!currentQuiz ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
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

      {/* Particles Background */}
      <Particles
        className="absolute inset-0 z-0"
        quantity={50}
        color="#3b82f6"
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 relative z-10">
        {/* Messages History - Show only last 2 messages */}
        {messages.length > 0 && !currentQuiz && (
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
          </div>
        )}

        {/* Loading Spinner - Show while waiting for backend response */}
        {isWaitingForResponse && !currentQuiz && (
          <div className="text-center mb-8">
            <LoaderOne />
          </div>
        )}

        {/* Persistent Video Player */}
        {currentVideoUrl && (
          <div className="mb-8 max-w-7xl mx-auto">
            <div className="relative w-full" style={{ aspectRatio: '16/9', minHeight: '500px' }}>
              <video 
                src={currentVideoUrl} 
                autoPlay 
                muted
                loop
                playsInline
                className="absolute inset-0 w-full h-full object-cover rounded-[2rem] shadow-2xl"
              >
                Your browser does not support the video tag.
              </video>
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

        {/* Input Field - Always visible but disabled during animations */}
        <div className="w-full max-w-5xl">
          <Input
            ref={inputRef}
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder=""
            className="text-center text-4xl font-light border-none shadow-none focus:ring-0 focus:border-none bg-transparent py-12 px-6"
            disabled={isTyping || isTransitioning || isWaitingForResponse || !!currentQuiz}
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