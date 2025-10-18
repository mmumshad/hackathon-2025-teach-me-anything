"""
ElevenLabs Text-to-Speech Service
Handles audio generation using ElevenLabs API
"""

import requests
import logging
from typing import Optional, Dict, Any
import os
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """Service for ElevenLabs Text-to-Speech integration"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice - good for educational content
        self.headers = {
            'xi-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def generate_audio(self, text: str, voice_id: Optional[str] = None) -> Optional[str]:
        """
        Generate audio from text using ElevenLabs TTS
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (optional, uses default if not provided)
            
        Returns:
            Base64 encoded audio data or None if failed
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not found. Audio generation disabled.")
            return None
        
        try:
            # Use default voice if none provided
            voice = voice_id or self.default_voice_id
            
            # Prepare the request
            url = f"{self.base_url}/text-to-speech/{voice}"
            
            # Voice settings optimized for educational content
            data = {
                "text": text,
                "voice_settings": {
                    "stability": 0.75,  # Balanced stability for clarity
                    "clarity": 0.9,     # High clarity for educational content
                    "similarity_boost": 0.8  # Maintain voice consistency
                }
            }
            
            logger.info(f"Generating audio for text: {text[:100]}...")
            
            # Make the API request
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                # Convert audio to base64 for storage/transmission
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                logger.info("Successfully generated audio with ElevenLabs")
                return audio_base64
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("ElevenLabs API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"ElevenLabs API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in ElevenLabs service: {str(e)}")
            return None
    
    def get_available_voices(self) -> Optional[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs
        
        Returns:
            Dictionary containing available voices or None if failed
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not found. Cannot fetch voices.")
            return None
        
        try:
            url = f"{self.base_url}/voices"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                voices_data = response.json()
                logger.info(f"Retrieved {len(voices_data.get('voices', []))} voices from ElevenLabs")
                return voices_data
            else:
                logger.error(f"Failed to fetch voices: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching voices: {str(e)}")
            return None
    
    async def get_voice_by_name(self, voice_name: str) -> Optional[str]:
        """
        Get voice ID by voice name
        
        Args:
            voice_name: Name of the voice to find
            
        Returns:
            Voice ID or None if not found
        """
        voices_data = await self.get_available_voices()
        if not voices_data:
            return None
        
        for voice in voices_data.get('voices', []):
            if voice.get('name', '').lower() == voice_name.lower():
                return voice.get('voice_id')
        
        logger.warning(f"Voice '{voice_name}' not found")
        return None
    
    def get_educational_voice_settings(self) -> Dict[str, float]:
        """
        Get voice settings optimized for educational content
        
        Returns:
            Dictionary with voice settings
        """
        return {
            "stability": 0.75,      # Balanced stability for clarity
            "clarity": 0.9,         # High clarity for educational content
            "similarity_boost": 0.8 # Maintain voice consistency
        }
    
    def get_storytelling_voice_settings(self) -> Dict[str, float]:
        """
        Get voice settings optimized for storytelling content
        
        Returns:
            Dictionary with voice settings
        """
        return {
            "stability": 0.6,       # More variation for storytelling
            "clarity": 0.85,        # Good clarity but more expressive
            "similarity_boost": 0.7 # Allow more voice variation
        }
