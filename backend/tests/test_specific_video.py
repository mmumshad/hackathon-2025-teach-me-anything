#!/usr/bin/env python3
"""
Test script for specific detailed video generation with exact instructions
"""

import asyncio
import time
import requests
import json
from pathlib import Path

# Specific video generation test
# Specific video generation test
SPECIFIC_PROMPT = (
    "A professional and friendly young Black woman with a voluminous, dark afro hairstyle, "
    "a warm, engaging smile, and wearing a mustard yellow knitted sweater. "
    "She should be presented as an educational presenter, speaking clearly and confidently, "
    "positioned in front of a plain white background. "
    "The video should show her explaining how adding 3 and 2 gives us 5. "
    "She should point to visual elements showing 3 apples and 2 apples, "
    "then demonstrate combining them to make 5 apples total. "
    "The narration should be: \"Here we have 3 and 2 apples. If we add them together we get 5.\" "
    "The video should be clear, educational, and engaging for young learners."
)

# Illustration-focused version without instructor
ILLUSTRATION_PROMPT = (
    "An educational animation showing a plain white background with clear, colorful visual elements. "
    "The video should demonstrate how adding 3 and 2 gives us 5 using bright red apples. "
    "Start by showing 3 apples on the left side of the screen, then show 2 apples on the right side. "
    "Animate the apples moving together and combining to form a group of 5 apples. "
    "Display the numbers 3, 2, and 5 clearly on screen with a plus sign and equals sign. "
    "The narration should be: \"Here we have 3 and 2 apples. If we add them together we get 5.\" "
    "The animation should be smooth, colorful, and engaging for young learners. "
    "Focus on clear visual storytelling without any instructor on screen."
)

API_BASE_URL = "http://localhost:8000/api/v1"
USER_ID = "test-user-specific"

async def generate_specific_video(use_illustration=False):
    """Generate video with specific detailed instructions"""
    
    prompt_type = "illustration-focused" if use_illustration else "instructor-based"
    prompt = ILLUSTRATION_PROMPT if use_illustration else SPECIFIC_PROMPT
    
    print(f"🎬 Testing {prompt_type} video generation...")
    print("📋 Topic: Math addition (3 + 2 = 5)")
    print("🎯 Specific requirements:")
    if use_illustration:
        print("   - Plain white background")
        print("   - Animated apples (3 + 2 = 5)")
        print("   - Numbers and symbols on screen")
        print("   - Smooth animation without instructor")
        print("   - Focus on visual storytelling")
    else:
        print("   - Plain white background")
        print("   - Show 3 apples and 2 apples")
        print("   - Demonstrate combining to make 5")
        print("   - Instructor pointing to visuals")
        print("   - Professional presenter")
    print("   - Specific narration script")
    print("   - 8 second duration")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Send specific video generation request
        message_content = "Create an illustration-focused video teaching math addition" if use_illustration else "Create a video teaching math addition with specific instructions"
        
        response = requests.post(
            f"{API_BASE_URL}/chat/message",
            headers={
                "Content-Type": "application/json",
                "X-User-ID": USER_ID
            },
            json={
                "message": {
                    "id": f"msg-{'illustration' if use_illustration else 'instructor'}",
                    "userId": USER_ID,
                    "content": message_content,
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "requireAudio": False
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Error generating video: {response.status_code}")
            return None
            
        data = response.json()
        video_id = data["responses"][0]["video"]["videoId"]
        video_prompt = data["responses"][0]["video"]["prompt"]
        
        print(f"✅ Video generation started: {video_id}")
        print(f"📝 Generated prompt:")
        print(f"   {video_prompt}")
        print("-" * 60)
        
        # Poll for completion
        generation_start = time.time()
        while True:
            await asyncio.sleep(7)  # Poll every 7 seconds
            
            status_response = requests.get(f"{API_BASE_URL}/video/{video_id}/status")
            if status_response.status_code != 200:
                print(f"❌ Error checking status")
                break
                
            status_data = status_response.json()
            video_status = status_data["video"]["status"]
            
            print(f"📊 Video status: {video_status}")
            
            if video_status == "completed":
                generation_time = time.time() - generation_start
                total_time = time.time() - start_time
                
                print(f"🎉 Video completed!")
                print(f"⏱️  Generation time: {generation_time:.2f} seconds")
                print(f"⏱️  Total time: {total_time:.2f} seconds")
                
                # Download the video
                download_response = requests.get(f"{API_BASE_URL}/video/{video_id}")
                if download_response.status_code == 200:
                    downloads_dir = Path("downloads")
                    downloads_dir.mkdir(exist_ok=True)
                    
                    video_filename = f"{'illustration' if use_illustration else 'instructor'}_math_addition_3plus2_{video_id}.mp4"
                    video_path = downloads_dir / video_filename
                    
                    with open(video_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"💾 Video downloaded: {video_path}")
                    print(f"📊 File size: {video_path.stat().st_size:,} bytes")
                    
                    return {
                        "video_id": video_id,
                        "generation_time": generation_time,
                        "total_time": total_time,
                        "file_path": str(video_path),
                        "file_size": video_path.stat().st_size,
                        "prompt": video_prompt
                    }
                else:
                    print(f"❌ Error downloading video")
                    return None
                    
            elif video_status == "failed":
                error_info = status_data["video"].get("error", {})
                print(f"❌ Video generation failed")
                print(f"   Error: {error_info.get('message', 'Unknown error')}")
                return None
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def main():
    """Main test function"""
    print("🚀 Starting specific video generation test")
    print("🎯 Goal: Test detailed instructional video generation")
    print("📚 Subject: Math addition (3 + 2 = 5)")
    print("⏱️  Duration: 8 seconds")
    print("🎨 Background: Plain white")
    print("👩 Presenter: Consistent description-based")
    print()
    
    # Test instructor-based version
    print("=" * 60)
    print("TEST 1: INSTRUCTOR-BASED VERSION")
    print("=" * 60)
    result1 = await generate_specific_video(use_illustration=False)
    
    if result1:
        print(f"\n✅ Instructor-based video generated!")
        print(f"📁 File: {result1['file_path']}")
        print(f"📊 Size: {result1['file_size']:,} bytes")
    
    print("\n" + "=" * 60)
    print("TEST 2: ILLUSTRATION-FOCUSED VERSION")
    print("=" * 60)
    result2 = await generate_specific_video(use_illustration=True)
    
    if result2:
        print(f"\n✅ Illustration-focused video generated!")
        print(f"📁 File: {result2['file_path']}")
        print(f"📊 Size: {result2['file_size']:,} bytes")
    
    # Summary
    print("\n" + "="*60)
    print("📊 COMPARISON SUMMARY")
    print("="*60)
    
    if result1 and result2:
        print("✅ Both videos generated successfully!")
        print(f"🎬 Instructor-based: {result1['generation_time']:.2f}s, {result1['file_size']:,} bytes")
        print(f"🎨 Illustration-focused: {result2['generation_time']:.2f}s, {result2['file_size']:,} bytes")
        print("\n🎉 Both video generation tests completed!")
    elif result1:
        print("✅ Instructor-based video generated successfully!")
        print("❌ Illustration-focused video failed")
    elif result2:
        print("❌ Instructor-based video failed")
        print("✅ Illustration-focused video generated successfully!")
    else:
        print("❌ Both tests failed!")

if __name__ == "__main__":
    asyncio.run(main())
