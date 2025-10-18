'use client';

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { generateUUID, getStoredUserId, storeUserId } from '@/lib/utils';
import ApiClient, { type ChatMessage, type ChatResponse } from '@/lib/api';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingText, setTypingText] = useState('');
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [userId, setUserId] = useState<string>('');
  const [apiClient, setApiClient] = useState<ApiClient | null>(null);
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
          setCurrentMessage(typingText.substring(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(interval);
          // Start transition immediately
          setIsTransitioning(true);
          setIsTyping(false);
          
          // Move message up and change to small text after typing completes
          setTimeout(() => {
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
    setIsWaitingForResponse(true);

    try {
      const message: ChatMessage = {
        id: generateUUID(),
        userId: userId,
        content: userMessage,
        timestamp: new Date().toISOString()
      };

      const data = await apiClient.sendMessage(message, false);
      // Start typing animation for the response
      setTypingText(data.response.content);
      setIsTyping(true);
    } catch (error) {
      console.error('Error sending message:', error);
      setTypingText('Sorry, I encountered an error. Please try again.');
      setIsTyping(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {/* Messages History */}
        {messages.length > 0 && (
          <div className="w-full max-w-4xl mb-8 space-y-6">
            {messages.map((message) => (
              <div key={message.id} className="text-lg text-gray-600 text-center leading-relaxed">
                {message.content}
              </div>
            ))}
          </div>
        )}

        {/* Current Typing Message */}
        {(isTyping || isTransitioning) && (
          <div className="text-center mb-8">
            <div className={`font-light leading-relaxed max-w-5xl mx-auto transition-all duration-1000 ease-in-out ${
              isTyping 
                ? 'text-5xl text-gray-800' 
                : 'text-lg text-gray-600'
            }`}>
              {currentMessage}
              {isTyping && <span className="animate-pulse text-gray-500">|</span>}
            </div>
          </div>
        )}

        {/* Input Field */}
        {!isTyping && !isTransitioning && (
          <div className="w-full max-w-5xl">
            <Input
              ref={inputRef}
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder=""
              className="text-center text-4xl font-light border-none shadow-none focus:ring-0 focus:border-none bg-transparent py-12 px-6"
              disabled={isWaitingForResponse}
              style={{ fontSize: '2.5rem', lineHeight: '1.4' }}
            />
          </div>
        )}

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