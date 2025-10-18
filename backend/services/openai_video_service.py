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
        self.demo_mode = Config.DEMO_MODE
        self.demo_video_path = Path("downloads/video_68f3cc10a178819182dea41f5260df460e238e5d025fc0e1.mp4")
        
        if not self.demo_mode and not self.openai_api_key:
            raise ValueError("OpenAI API key is required but not found in configuration")
        
        if not self.demo_mode:
            self.client = openai.OpenAI(api_key=self.openai_api_key)
    
    async def generate_video(
        self, 
        prompt: str, 
        model: str = "sora-2",
        size: str = "720x1280",
        seconds: str = "8"
    ) -> Dict[str, Any]:
        """
        Generate video using OpenAI Sora 2 or return demo video
        
        Args:
            prompt: Text description of the video to generate
            model: Sora model to use
            size: Video size (720x1280, 1280x720, 1024x1792, 1792x1024)
            seconds: Video duration ("4", "8", or "12")
            
        Returns:
            Dictionary with video information
        """
        try:
            # Demo mode - return demo video immediately
            if self.demo_mode:
                import uuid
                demo_video_id = f"demo_{uuid.uuid4().hex[:16]}"
                
                return {
                    "provider": "demo",
                    "id": demo_video_id,
                    "object": "video",
                    "model": "demo-model",
                    "status": "completed",  # Demo video is immediately available
                    "progress": 100,
                    "created_at": int(time.time()),
                    "size": size,
                    "seconds": seconds,
                    "prompt": prompt,
                    "demo_mode": True
                }
            
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
            # Demo mode - return demo video status
            if self.demo_mode and video_id.startswith("demo_"):
                return {
                    "provider": "demo",
                    "id": video_id,
                    "object": "video",
                    "model": "demo-model",
                    "status": "completed",
                    "progress": 100,
                    "created_at": int(time.time()),
                    "size": "1280x720",
                    "seconds": "12",
                    "checked_at": time.time(),
                    "demo_mode": True
                }
            
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
            # Demo mode - return demo video file
            if self.demo_mode and video_id.startswith("demo_"):
                if self.demo_video_path.exists():
                    return self.demo_video_path
                else:
                    raise ValueError(f"Demo video file not found: {self.demo_video_path}")
            
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
        if self.demo_mode:
            return self.demo_video_path.exists()
        return self.openai_api_key is not None
