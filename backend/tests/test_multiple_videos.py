#!/usr/bin/env python3
"""
Test script for generating multiple videos with presenter reference image
Measures generation times and downloads completed videos
"""

import asyncio
import time
import requests
import json
from pathlib import Path
import os

# Test topics for video generation (reduced for quick test)
TEST_TOPICS = [
    "math basics",
    "colors and shapes"
]

API_BASE_URL = "http://localhost:8000/api/v1"
USER_ID = "test-user-multiple"

async def generate_video(topic: str, index: int):
    """Generate a single video and measure timing"""
    print(f"\n🎬 Starting video {index + 1}/5: {topic}")
    start_time = time.time()
    
    try:
        # Send video generation request
        response = requests.post(
            f"{API_BASE_URL}/chat/message",
            headers={
                "Content-Type": "application/json",
                "X-User-ID": USER_ID
            },
            json={
                "message": {
                    "id": f"msg-{index}",
                    "userId": USER_ID,
                    "content": f"Create a video about {topic}",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "requireAudio": False
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Error generating video {index + 1}: {response.status_code}")
            return None
            
        data = response.json()
        video_id = data["responses"][0]["video"]["videoId"]
        print(f"✅ Video {index + 1} generation started: {video_id}")
        
        # Poll for completion
        generation_start = time.time()
        while True:
            await asyncio.sleep(7)  # Poll every 7 seconds
            
            status_response = requests.get(f"{API_BASE_URL}/video/{video_id}/status")
            if status_response.status_code != 200:
                print(f"❌ Error checking status for video {index + 1}")
                break
                
            status_data = status_response.json()
            video_status = status_data["video"]["status"]
            
            print(f"📊 Video {index + 1} status: {video_status}")
            
            if video_status == "completed":
                generation_time = time.time() - generation_start
                total_time = time.time() - start_time
                
                print(f"🎉 Video {index + 1} completed!")
                print(f"⏱️  Generation time: {generation_time:.2f} seconds")
                print(f"⏱️  Total time: {total_time:.2f} seconds")
                
                # Download the video
                download_response = requests.get(f"{API_BASE_URL}/video/{video_id}")
                if download_response.status_code == 200:
                    downloads_dir = Path("downloads")
                    downloads_dir.mkdir(exist_ok=True)
                    
                    video_filename = f"video_{index + 1}_{topic.replace(' ', '_')}_{video_id}.mp4"
                    video_path = downloads_dir / video_filename
                    
                    with open(video_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"💾 Video {index + 1} downloaded: {video_path}")
                    return {
                        "topic": topic,
                        "video_id": video_id,
                        "generation_time": generation_time,
                        "total_time": total_time,
                        "file_path": str(video_path),
                        "file_size": video_path.stat().st_size
                    }
                else:
                    print(f"❌ Error downloading video {index + 1}")
                    return None
                    
            elif video_status == "failed":
                print(f"❌ Video {index + 1} generation failed")
                return None
                
    except Exception as e:
        print(f"❌ Error with video {index + 1}: {str(e)}")
        return None

async def main():
    """Main test function"""
    print("🚀 Starting multiple video generation test")
    print(f"📋 Topics: {', '.join(TEST_TOPICS)}")
    print(f"⏱️  Polling interval: 7 seconds")
    print(f"🎬 Video duration: 4 seconds")
    print(f"👩 Presenter: Description-based (consistent presenter)")
    
    start_time = time.time()
    results = []
    
    # Generate videos sequentially (not parallel to avoid overwhelming the API)
    for i, topic in enumerate(TEST_TOPICS):
        result = await generate_video(topic, i)
        if result:
            results.append(result)
        
        # Small delay between requests
        if i < len(TEST_TOPICS) - 1:
            print("⏳ Waiting 5 seconds before next video...")
            await asyncio.sleep(5)
    
    total_time = time.time() - start_time
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Videos generated: {len(results)}/{len(TEST_TOPICS)}")
    print(f"⏱️  Total test time: {total_time:.2f} seconds")
    print(f"📁 Videos saved to: downloads/")
    
    if results:
        print("\n📋 Individual Results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['topic']}")
            print(f"     Generation: {result['generation_time']:.2f}s")
            print(f"     File: {result['file_path']}")
            print(f"     Size: {result['file_size']:,} bytes")
        
        avg_generation_time = sum(r['generation_time'] for r in results) / len(results)
        print(f"\n📈 Average generation time: {avg_generation_time:.2f} seconds")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
