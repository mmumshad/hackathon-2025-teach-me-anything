"""
OpenAI Sora 2 Video Generation Service
Handles video generation using OpenAI's Sora 2 API
"""

import openai
import time
import asyncio
from typing import Dict, Optional, Any, List
from pathlib import Path
from config import Config

class OpenAIVideoService:
    """Service class for OpenAI Sora 2 video generation"""
    
    def __init__(self):
        """Initialize OpenAI video service"""
        self.openai_api_key = Config.OPENAI_API_KEY
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required but not found in configuration")
        
        self.client = openai.OpenAI(api_key=self.openai_api_key)
    
    async def generate_video(
        self, 
        prompt: str, 
        model: str = "sora-2",
        size: str = "720x1280",
        seconds: str = "8"
    ) -> Dict[str, Any]:
        """
        Generate video using OpenAI Sora 2
        
        Args:
            prompt: Text description of the video to generate
            model: Sora model to use
            size: Video size (720x1280, 1280x720, 1024x1792, 1792x1024)
            seconds: Video duration ("4", "8", or "12")
            
        Returns:
            Dictionary with video information
        """
        try:
            # Validate parameters
            if size not in self.get_valid_sizes():
                raise ValueError(f"Invalid size: {size}. Valid sizes: {self.get_valid_sizes()}")
            
            if seconds not in self.get_valid_durations():
                raise ValueError(f"Invalid duration: {seconds}. Valid durations: {self.get_valid_durations()}")
            
            # Real OpenAI Sora 2 API call
            response = self.client.videos.create(
                prompt=prompt,
                model=model,
                size=size,
                seconds=seconds
            )
            
            return {
                "provider": "sora2",
                "id": response.id,
                "object": response.object,
                "model": response.model,
                "status": response.status,
                "progress": getattr(response, 'progress', 0),
                "created_at": response.created_at,
                "size": getattr(response, 'size', size),
                "seconds": getattr(response, 'seconds', seconds),
                "prompt": prompt
            }
            
        except Exception as e:
            raise Exception(f"Error generating video with Sora 2: {str(e)}")
    
    async def check_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job
        
        Args:
            video_id: Video ID to check
            
        Returns:
            Dictionary with status information
        """
        try:
            # Real OpenAI Sora 2 API call
            video = self.client.videos.retrieve(video_id)
            
            response_data = {
                "provider": "sora2",
                "id": video.id,
                "object": video.object,
                "model": video.model,
                "status": video.status,
                "progress": getattr(video, 'progress', 0),
                "created_at": video.created_at,
                "size": getattr(video, 'size', '720x1280'),
                "seconds": getattr(video, 'seconds', '8'),
                "checked_at": time.time()
            }
            
            if video.status == "completed":
                response_data["completed_at"] = getattr(video, 'completed_at', None)
                response_data["expires_at"] = getattr(video, 'expires_at', None)
            elif video.status == "failed":
                response_data["error"] = getattr(video, 'error', 'Unknown error')
            
            return response_data
            
        except Exception as e:
            raise Exception(f"Error checking Sora 2 status: {str(e)}")
    
    async def wait_for_completion(
        self, 
        video_id: str, 
        max_wait_time: int = 300,
        check_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for video generation to complete
        
        Args:
            video_id: Video ID to monitor
            max_wait_time: Maximum time to wait in seconds
            check_interval: Time between status checks in seconds
            
        Returns:
            Final status dictionary
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = await self.check_status(video_id)
            
            if status["status"] in ["completed", "failed"]:
                return status
            
            await asyncio.sleep(check_interval)
        
        # Timeout reached
        return {
            "provider": "sora2",
            "id": video_id,
            "status": "timeout",
            "error": f"Video generation timed out after {max_wait_time} seconds",
            "checked_at": time.time()
        }
    
    async def download_video(self, video_id: str, save_path: Optional[str] = None) -> Optional[Path]:
        """
        Download a completed video
        
        Args:
            video_id: Video ID to download
            save_path: Optional custom save path
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Check if video is completed
            status = await self.check_status(video_id)
            if status["status"] != "completed":
                raise ValueError(f"Video is not completed. Status: {status['status']}")
            
            # Download video content
            response = self.client.videos.download_content(video_id=video_id)
            content = response.read()
            
            # Determine save path
            if save_path:
                filepath = Path(save_path)
            else:
                downloads_dir = Path("downloads")
                downloads_dir.mkdir(exist_ok=True)
                filepath = downloads_dir / f"{video_id}.mp4"
            
            # Save the video
            with open(filepath, 'wb') as f:
                f.write(content)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error downloading video: {str(e)}")
    
    async def list_videos(self) -> List[Dict[str, Any]]:
        """
        List all videos
        
        Returns:
            List of video information dictionaries
        """
        try:
            videos = self.client.videos.list()
            
            video_list = []
            for video in videos.data:
                video_info = {
                    "id": video.id,
                    "object": video.object,
                    "model": video.model,
                    "status": video.status,
                    "created_at": getattr(video, 'created_at', None),
                    "progress": getattr(video, 'progress', 0),
                    "size": getattr(video, 'size', None),
                    "seconds": getattr(video, 'seconds', None)
                }
                
                if video.status == "completed":
                    video_info["completed_at"] = getattr(video, 'completed_at', None)
                    video_info["expires_at"] = getattr(video, 'expires_at', None)
                elif video.status == "failed":
                    video_info["error"] = getattr(video, 'error', None)
                
                video_list.append(video_info)
            
            return video_list
            
        except Exception as e:
            raise Exception(f"Error listing videos: {str(e)}")
    
    def get_valid_sizes(self) -> List[str]:
        """Get list of valid video sizes for Sora 2"""
        return ["720x1280", "1280x720", "1024x1792", "1792x1024"]
    
    def get_valid_durations(self) -> List[str]:
        """Get list of valid video durations for Sora 2"""
        return ["4", "8", "12"]
    
    def is_available(self) -> bool:
        """Check if OpenAI video service is available"""
        return self.openai_api_key is not None
