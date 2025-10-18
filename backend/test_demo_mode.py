#!/usr/bin/env python3
"""
Test script for Demo Mode functionality
Tests video generation in demo mode vs normal mode
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set DEMO_MODE environment variable BEFORE importing modules
os.environ["DEMO_MODE"] = "true"

from services.openai_video_service import OpenAIVideoService
from config import Config

async def test_demo_mode():
    """Test demo mode functionality"""
    print("🧪 Testing Demo Mode Functionality")
    print("=" * 50)
    
    # Test 1: Check if demo video file exists
    demo_video_path = Path("downloads/video_68f3cc10a178819182dea41f5260df460e238e5d025fc0e1.mp4")
    print(f"📁 Demo video file exists: {demo_video_path.exists()}")
    if demo_video_path.exists():
        file_size = demo_video_path.stat().st_size
        print(f"📊 Demo video file size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
    
    # Test 2: Test with DEMO_MODE=true (already set above)
    print("\n🎬 Testing with DEMO_MODE=true")
    
    try:
        video_service = OpenAIVideoService()
        print(f"✅ Video service initialized successfully")
        print(f"🔧 Demo mode enabled: {video_service.demo_mode}")
        print(f"📹 Service available: {video_service.is_available()}")
        
        # Test video generation
        print("\n🎥 Testing video generation...")
        video_result = await video_service.generate_video(
            prompt="A beautiful sunset over mountains",
            model="sora-2",
            size="1280x720",
            seconds="12"
        )
        
        print(f"📋 Video generation result:")
        print(f"   ID: {video_result['id']}")
        print(f"   Status: {video_result['status']}")
        print(f"   Provider: {video_result['provider']}")
        print(f"   Demo mode: {video_result.get('demo_mode', False)}")
        
        # Test status check
        print("\n🔍 Testing status check...")
        status_result = await video_service.check_status(video_result['id'])
        print(f"📊 Status check result:")
        print(f"   Status: {status_result['status']}")
        print(f"   Progress: {status_result['progress']}%")
        print(f"   Demo mode: {status_result.get('demo_mode', False)}")
        
        # Test video download
        print("\n⬇️ Testing video download...")
        download_result = await video_service.download_video(video_result['id'])
        print(f"📁 Download result: {download_result}")
        print(f"📊 Downloaded file exists: {download_result.exists()}")
        if download_result.exists():
            print(f"📏 Downloaded file size: {download_result.stat().st_size:,} bytes")
        
        print("\n✅ Demo mode test completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo mode test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test with DEMO_MODE=false (normal mode)
    print("\n" + "=" * 50)
    print("🎬 Testing with DEMO_MODE=false")
    os.environ["DEMO_MODE"] = "false"
    
    # Reload config
    import importlib
    import config
    importlib.reload(config)
    Config = config.Config
    
    try:
        video_service = OpenAIVideoService()
        print(f"✅ Video service initialized successfully")
        print(f"🔧 Demo mode enabled: {video_service.demo_mode}")
        print(f"📹 Service available: {video_service.is_available()}")
        
        print("\n✅ Normal mode test completed!")
        
    except Exception as e:
        print(f"❌ Normal mode test failed: {str(e)}")
        print("   This is expected if OpenAI API key is not configured")

if __name__ == "__main__":
    asyncio.run(test_demo_mode())
