"""
Configuration module for TechMeAnything API
Handles environment variables and API key management
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv(".env")

class Config:
    """Configuration class for API settings and credentials"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    
    # Gemini Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Mem0 Configuration
    MEM0_API_KEY: Optional[str] = os.getenv("MEM0_API_KEY")
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_MCP_API_KEY: Optional[str] = os.getenv("SUPABASE_MCP_API_KEY")
    
    # Server Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "False").lower() == "true"
    
    # API Settings
    MAX_RESPONSE_LENGTH: int = int(os.getenv("MAX_RESPONSE_LENGTH", "1000"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required API keys are present"""
        required_keys = ["OPENAI_API_KEY"]
        missing_keys = []
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        return True

# Validate configuration on import
try:
    Config.validate_config()
    print("✅ Configuration validated successfully")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("Please check your .env file and ensure all required API keys are set.")
