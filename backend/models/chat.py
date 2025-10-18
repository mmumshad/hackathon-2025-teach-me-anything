"""
Chat models for TechMeAnything API
Contains Pydantic models for chat-related data structures
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi import UploadFile

class ChatMessage(BaseModel):
    """Model for chat messages"""
    id: str
    userId: str
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    """Model for chat requests"""
    message: ChatMessage
    requireAudio: Optional[bool] = False
    attachedFile: Optional[str] = None  # File path or reference for attached PDF

class QuizOption(BaseModel):
    """Model for quiz options"""
    id: str
    text: str

class QuizQuestion(BaseModel):
    """Model for quiz questions"""
    id: str
    question: str
    options: List[QuizOption]
    correctAnswerId: str
    explanation: str

class ChatResponse(BaseModel):
    """Model for individual chat responses"""
    id: str
    messageId: str
    content: str
    timestamp: str
    audioUrl: Optional[str] = None
    audiobookChunks: Optional[List[str]] = None  # Base64 encoded audio chunks for audiobook
    audiobookInfo: Optional[Dict[str, Any]] = None  # Info about the generated audiobook

class ChatMessageResponse(BaseModel):
    """Model for complete chat message responses"""
    success: bool
    response: ChatResponse
    audioUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    quiz: Optional[List[QuizQuestion]] = None

class FileUploadResponse(BaseModel):
    """Model for file upload responses"""
    success: bool
    fileId: str
    fileName: str
    filePath: str
    fileSize: int
    message: str
