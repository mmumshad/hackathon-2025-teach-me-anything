#!/usr/bin/env python3
"""
Simple test for the OpenAI video service
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.openai_video_service import OpenAIVideoService

async def test_openai_video():
    """Test the OpenAI video service"""
    
    print("🎬 Testing OpenAI Video Service")
    print("=" * 40)
    
    try:
        # Create service
        service = OpenAIVideoService()
        
        print("✅ Service created successfully!")
        print(f"📋 Valid sizes: {service.get_valid_sizes()}")
        print(f"📋 Valid durations: {service.get_valid_durations()}")
        
        # Generate a simple video
        print(f"\n🎬 Generating video...")
        result = await service.generate_video(
            prompt="A simple test video",
            size="720x1280",
            seconds="4"
        )
        
        print(f"✅ Video generation started!")
        print(f"   ID: {result['id']}")
        print(f"   Status: {result['status']}")
        
        # Check status
        print(f"\n⏳ Checking status...")
        status = await service.check_status(result['id'])
        print(f"   Status: {status['status']}")
        print(f"   Progress: {status.get('progress', 0)}%")
        
        # List videos
        print(f"\n📋 Listing videos...")
        videos = await service.list_videos()
        print(f"   Found {len(videos)} videos")
        
        print(f"\n🎯 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 OpenAI Video Service Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("../services/openai_video_service.py").exists() and not Path("services/openai_video_service.py").exists():
        print("❌ Error: Please run this script from the backend or tests directory")
        exit(1)
    
    # Run the test
    asyncio.run(test_openai_video())
