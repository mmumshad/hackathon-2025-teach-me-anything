#!/usr/bin/env python3
"""
Test video service: Create 16:9 educational video about planets for kids
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.openai_video_service import OpenAIVideoService

async def create_planets_video():
    """Create an educational video about planets for kids"""
    
    print("🪐 Creating Educational Video: Planets for Kids")
    print("=" * 60)
    
    try:
        # Create service
        service = OpenAIVideoService()
        print("✅ OpenAI Video Service initialized!")
        
        # Define the educational prompt for kids
        prompt = """An animated educational video explaining planets to kids. 
        Show colorful planets orbiting the sun, with simple animations and 
        child-friendly graphics. Include Mercury, Venus, Earth, Mars, Jupiter, 
        Saturn, Uranus, and Neptune. Use bright colors and simple shapes that 
        kids can understand. Add gentle background music and friendly narration 
        style suitable for children ages 6-10."""
        
        print(f"\n🎬 Generating 16:9 video...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Generate video with 16:9 aspect ratio (1280x720)
        result = await service.generate_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",  # 16:9 aspect ratio
            seconds="8"       # 8 seconds for educational content
        )
        
        print(f"✅ Video generation started!")
        print(f"   🆔 Video ID: {result['id']}")
        print(f"   📊 Status: {result['status']}")
        print(f"   📐 Size: {result['size']} (16:9)")
        print(f"   ⏱️ Duration: {result['seconds']} seconds")
        print(f"   🤖 Model: {result['model']}")
        
        video_id = result['id']
        
        # Wait for completion with progress updates
        print(f"\n⏳ Waiting for video completion...")
        print(f"   This may take a few minutes...")
        
        final_result = await service.wait_for_completion(
            video_id=video_id,
            max_wait_time=600,  # Wait up to 10 minutes
            check_interval=15   # Check every 15 seconds
        )
        
        print(f"\n🏁 Final Status:")
        print(f"   Status: {final_result['status']}")
        
        if final_result['status'] == 'completed':
            print(f"   🎉 Video completed successfully!")
            print(f"   📊 Progress: {final_result.get('progress', 100)}%")
            
            # Download the video
            print(f"\n📥 Downloading video...")
            downloaded_path = await service.download_video(video_id)
            
            if downloaded_path:
                print(f"   ✅ Video downloaded successfully!")
                print(f"   📁 File path: {downloaded_path}")
                print(f"   📏 File size: {downloaded_path.stat().st_size / (1024*1024):.1f} MB")
                
                # Show file info
                print(f"\n📋 Video Information:")
                print(f"   🆔 ID: {video_id}")
                print(f"   📐 Resolution: 1280x720 (16:9)")
                print(f"   ⏱️ Duration: 8 seconds")
                print(f"   🎯 Content: Educational planets video for kids")
                print(f"   📁 Location: {downloaded_path}")
                
                return downloaded_path
            else:
                print(f"   ❌ Download failed!")
                return None
                
        elif final_result['status'] == 'failed':
            print(f"   ❌ Video generation failed!")
            print(f"   Error: {final_result.get('error', 'Unknown error')}")
            return None
            
        elif final_result['status'] == 'timeout':
            print(f"   ⏰ Video generation timed out!")
            print(f"   The video might still be processing...")
            return None
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def check_recent_videos():
    """Check recent videos to see what's been generated"""
    
    print(f"\n📋 Checking Recent Videos...")
    print("-" * 40)
    
    try:
        service = OpenAIVideoService()
        videos = await service.list_videos()
        
        print(f"   Found {len(videos)} total videos")
        
        # Show recent videos
        for i, video in enumerate(videos[:5], 1):  # Show first 5
            status_emoji = "✅" if video['status'] == 'completed' else "⏳" if video['status'] == 'in_progress' else "❌"
            print(f"   {i}. {status_emoji} {video['id']} - {video['status']}")
            
    except Exception as e:
        print(f"   ❌ Error listing videos: {str(e)}")

if __name__ == "__main__":
    print("🚀 Educational Video Generator Test")
    print("=" * 60)
    print("🎯 Goal: Create 16:9 educational video about planets for kids")
    print("📋 Steps: Generate → Wait → Download")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("../services/openai_video_service.py").exists() and not Path("services/openai_video_service.py").exists():
        print("❌ Error: Please run this script from the backend or tests directory")
        exit(1)
    
    # Run the test
    result = asyncio.run(create_planets_video())
    
    # Check recent videos
    asyncio.run(check_recent_videos())
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"   Educational planets video created and downloaded!")
        print(f"   Ready to use in your educational app!")
    else:
        print(f"\n❌ Test completed with issues")
        print(f"   Check the error messages above")
