#!/usr/bin/env python3
"""
Test script to capture exact OpenAI error message with reference image
"""

import asyncio
import json
from datetime import datetime
from services.openai_video_service import OpenAIVideoService

async def test_reference_image_error():
    """Test video generation with reference image and capture exact error"""
    
    print("🧪 Testing video generation with reference image...")
    print("📸 Reference image: services/presenter.jpeg")
    print("🎬 Video size: 1280x720")
    print("⏱️ Duration: 4 seconds")
    print("-" * 60)
    
    video_service = OpenAIVideoService()
    
    try:
        result = await video_service.generate_video(
            prompt="Educational video about animals",
            model="sora-2",
            size="1280x720",
            seconds="4",
            reference_image_path="services/presenter.jpeg"
        )
        
        print("✅ SUCCESS: Video generation worked!")
        print(f"Video ID: {result['id']}")
        print(f"Status: {result['status']}")
        
    except Exception as e:
        print("❌ ERROR: Video generation failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Create detailed error report
        error_report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "reference_image_video_generation",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "video_parameters": {
                "prompt": "Educational video about animals",
                "model": "sora-2",
                "size": "1280x720",
                "seconds": "4",
                "reference_image_path": "services/presenter.jpeg"
            },
            "reference_image_info": {
                "path": "services/presenter.jpeg",
                "exists": True
            }
        }
        
        # Write error report to temporary file
        with open("temp_openai_error_report.json", "w") as f:
            json.dump(error_report, f, indent=2)
        
        print(f"\n📄 Error report saved to: temp_openai_error_report.json")
        print("📋 Full error details:")
        print(json.dumps(error_report, indent=2))

if __name__ == "__main__":
    asyncio.run(test_reference_image_error())
