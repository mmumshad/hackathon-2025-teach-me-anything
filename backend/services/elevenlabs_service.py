"""
ElevenLabs Text-to-Speech Service
Handles audio generation using ElevenLabs API
"""

import requests
import logging
from typing import Optional, Dict, Any, List
import os
from io import BytesIO
import base64
import re

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """Service for ElevenLabs Text-to-Speech integration"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "yj4ZLC16WtrBEwPzIXzI")  # Custom voice for educational content
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
    
    def split_text_for_audiobook(self, text: str, max_chunk_size: int = 4000) -> List[str]:
        """
        Split long text into chunks suitable for audiobook generation
        
        Args:
            text: Text to split
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the limit, start a new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk if it's not empty
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_audiobook(self, text: str, voice_id: Optional[str] = None) -> Optional[List[str]]:
        """
        Generate audiobook from long text by splitting into chunks and generating audio for each
        
        Args:
            text: Text to convert to audiobook
            voice_id: Voice ID to use (optional, uses default if not provided)
            
        Returns:
            List of base64 encoded audio chunks or None if failed
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not found. Audiobook generation disabled.")
            return None
        
        try:
            # Split text into manageable chunks
            text_chunks = self.split_text_for_audiobook(text)
            logger.info(f"Split text into {len(text_chunks)} chunks for audiobook generation")
            
            audio_chunks = []
            
            for i, chunk in enumerate(text_chunks):
                logger.info(f"Generating audio for chunk {i+1}/{len(text_chunks)}")
                
                # Generate audio for this chunk
                audio_data = self.generate_audio(chunk, voice_id)
                
                if audio_data:
                    audio_chunks.append(audio_data)
                else:
                    logger.error(f"Failed to generate audio for chunk {i+1}")
                    # Continue with other chunks even if one fails
                    continue
            
            if audio_chunks:
                logger.info(f"Successfully generated audiobook with {len(audio_chunks)} audio chunks")
                return audio_chunks
            else:
                logger.error("Failed to generate any audio chunks for audiobook")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error in audiobook generation: {str(e)}")
            return None
