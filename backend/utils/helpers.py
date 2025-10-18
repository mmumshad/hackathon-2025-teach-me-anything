"""
Helper utilities for TechMeAnything API
Contains utility functions for common operations
"""

import uuid
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def generate_user_id() -> str:
    """Generate a unique user ID"""
    return str(uuid.uuid4())

def detect_language(text: str) -> str:
    """Simple language detection based on common patterns"""
    # Basic language detection - can be enhanced with ML models
    if any(char in text for char in ['你好', '中文', '汉语']):
        return 'zh'
    elif any(char in text for char in ['है', 'हूं', 'कर', 'में']):
        return 'hi'
    elif any(char in text for char in ['hola', 'español', 'gracias']):
        return 'es'
    elif any(char in text for char in ['مرحبا', 'عربي', 'شكرا']):
        return 'ar'
    else:
        return 'en'  # Default to English

def log_api_call(func):
    """Decorator to log API call performance"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
