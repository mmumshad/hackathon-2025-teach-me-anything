"""
User models for TechMeAnything API
Contains Pydantic models for user-related data structures
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserPreferences(BaseModel):
    """Model for user preferences"""
    language: str = "en"
    muteAudio: bool = True
    learningLevel: str = "beginner"  # beginner, intermediate, advanced
    learningStyle: str = "visual"    # visual, auditory, kinesthetic
    preferredSubjects: List[str] = []

class UserProfile(BaseModel):
    """Model for user profiles"""
    userId: str
    userName: str
    gradeLevel: int
    preferences: UserPreferences
    createdAt: str
    lastActiveAt: str
