'use client';

import { useState } from 'react';
import { ChatResponse } from '@/lib/api';

interface QuizProps {
  quiz: ChatResponse['quiz'];
  onQuizComplete: () => void;
}

export function Quiz({ quiz, onQuizComplete }: QuizProps) {
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [quizResults, setQuizResults] = useState<Record<string, boolean>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const handleQuizAnswer = (questionId: string, answerId: string) => {
    if (quizResults[questionId]) return; // Don't allow changes after answering
    
    setQuizAnswers(prev => ({ ...prev, [questionId]: answerId }));
    
    // Check if answer is correct
    const question = quiz?.find(q => q.id === questionId);
    if (question) {
      const isCorrect = answerId === question.correctAnswerId;
      setQuizResults(prev => ({ ...prev, [questionId]: isCorrect }));
    }
  };

  const goToNextQuestion = () => {
    if (quiz && currentQuestionIndex < quiz.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else if (isLastQuestion) {
      // On the last question, complete the quiz
      onQuizComplete();
    }
  };

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  if (!quiz || quiz.length === 0) return null;

  const currentQuestion = quiz[currentQuestionIndex];
  const isFirstQuestion = currentQuestionIndex === 0;
  const isLastQuestion = currentQuestionIndex === quiz.length - 1;

  return (
    <div className="mb-8 w-full max-w-4xl mx-auto">
      {/* Question Progress */}
      <div className="text-center mb-6">
        <span className="text-sm text-gray-500">
          Question {currentQuestionIndex + 1} of {quiz.length}
        </span>
      </div>

      {/* Current Question */}
      <div className="bg-gray-50 rounded-2xl p-6 w-full min-h-[400px] flex flex-col">
        <h3 className="text-xl font-medium text-gray-800 mb-4 text-center">
          {currentQuestion.question}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {currentQuestion.options.map((option) => {
            const isSelected = quizAnswers[currentQuestion.id] === option.id;
            const isAnswered = quizResults[currentQuestion.id] !== undefined;
            const isCorrect = option.id === currentQuestion.correctAnswerId;
            const isWrong = isSelected && !isCorrect && isAnswered;
            
            let buttonClass = "w-full p-4 text-left rounded-xl border-2 transition-all duration-200 font-medium ";
            
            if (isAnswered) {
              if (isCorrect) {
                buttonClass += "bg-green-100 border-green-500 text-green-800";
              } else if (isWrong) {
                buttonClass += "bg-red-100 border-red-500 text-red-800";
              } else {
                buttonClass += "bg-gray-100 border-gray-300 text-gray-600";
              }
            } else {
              buttonClass += isSelected 
                ? "bg-blue-100 border-blue-500 text-blue-800" 
                : "bg-white border-gray-200 text-gray-700 hover:border-blue-300 hover:bg-blue-50";
            }
            
            return (
              <button
                key={option.id}
                onClick={() => handleQuizAnswer(currentQuestion.id, option.id)}
                disabled={isAnswered}
                className={buttonClass}
              >
                {option.text}
              </button>
            );
          })}
        </div>
        
        {/* Show explanation after answering */}
        <div className="mt-4 flex-1 flex flex-col">
          {quizResults[currentQuestion.id] !== undefined ? (
            <div className="p-4 bg-blue-50 rounded-xl border border-blue-200 flex-1 flex flex-col justify-center">
              <p className="text-blue-800 font-medium">
                {quizResults[currentQuestion.id] ? "✅ Correct!" : "❌ Incorrect"}
              </p>
              <p className="text-blue-700 mt-2">{currentQuestion.explanation}</p>
            </div>
          ) : (
            <div className="flex-1"></div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-6">
        <button
          onClick={goToPreviousQuestion}
          disabled={isFirstQuestion}
          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
            isFirstQuestion
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-blue-100 text-blue-700 hover:bg-blue-200"
          }`}
        >
          ← Previous
        </button>
        
        <button
          onClick={goToNextQuestion}
          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
            isLastQuestion
              ? "bg-green-100 text-green-700 hover:bg-green-200"
              : "bg-blue-100 text-blue-700 hover:bg-blue-200"
          }`}
        >
          {isLastQuestion ? "Complete Quiz" : "Next →"}
        </button>
      </div>
    </div>
  );
}
