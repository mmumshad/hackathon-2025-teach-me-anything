#!/usr/bin/env python3
"""
Test script for generating 5 illustration-focused educational videos
Each video has structured prompts with separate sections for design, narration, and content
"""

import asyncio
import time
import requests
import json
from pathlib import Path

# Video topics for generation - Math Operations Series
VIDEO_TOPICS = [
    {
        "topic": "math_addition",
        "title": "Math Addition (5 + 3 = 8)",
        "content": "5 red apples + 3 green apples = 8 apples total",
        "visual_description": "Show 5 red apples on the left, 3 green apples on the right, then animate them moving together to form a group of 8 apples",
        "equation": "5 + 3 = 8"
    },
    {
        "topic": "math_subtraction", 
        "title": "Math Subtraction (8 - 3 = 5)",
        "content": "8 apples total - 3 apples taken away = 5 apples left",
        "visual_description": "Start with 8 apples in a group, then animate 3 apples moving away or disappearing, leaving 5 apples remaining",
        "equation": "8 - 3 = 5"
    },
    {
        "topic": "math_multiplication",
        "title": "Math Multiplication (3 × 2 = 6)",
        "content": "3 groups of 2 apples each = 6 apples total",
        "visual_description": "Show 3 separate groups, each containing 2 apples, then count all apples together to show 6 total apples",
        "equation": "3 × 2 = 6"
    },
    {
        "topic": "math_division",
        "title": "Math Division (6 ÷ 2 = 3)",
        "content": "6 apples divided into 2 equal groups = 3 apples in each group",
        "visual_description": "Start with 6 apples together, then animate them splitting into 2 equal groups of 3 apples each",
        "equation": "6 ÷ 2 = 3"
    }
]

# Structured prompt sections
PROMPT_SECTIONS = {
    "design": (
        "An educational animation with a clean, plain white background. "
        "Use bright, colorful visual elements that are clear and engaging for young learners. "
        "All graphics should be simple, bold, and easy to understand."
    ),
    
    "instructor_voice": (
        "The narration should be delivered by a warm, friendly female voice with a clear, "
        "educational tone. The voice should sound like a young adult woman in her mid-20s, "
        "encouraging and engaging, perfect for children ages 4-8. "
        "Use a standard American accent that is clear and easy to understand. "
        "The voice should be enthusiastic but not overly excited, with a gentle, patient delivery."
    )
}

# Specific narration texts for each math operation video with continuity
NARRATION_TEXTS = {
    "math_addition": (
        "Welcome to our math series! Let's start with addition! "
        "Here we have 5 red apples. "
        "Now we add 3 green apples. "
        "When we put them together, we have 8 apples total. "
        "5 plus 3 equals 8!"
    ),
    
    "math_subtraction": (
        "Great job learning addition! Now we learn about subtraction! "
        "Here we start with 8 apples. "
        "Now we take away 3 apples. "
        "We are left with 5 apples. "
        "8 minus 3 equals 5!"
    ),
    
    "math_multiplication": (
        "Excellent! Now let's move on to multiplication! "
        "We have 3 groups of apples. "
        "Each group has 2 apples. "
        "When we count all the apples, we have 6 total. "
        "3 times 2 equals 6!"
    ),
    
    "math_division": (
        "Perfect! Finally, let's learn about division! "
        "Here we have 6 apples. "
        "We want to share them equally into 2 groups. "
        "Each group gets 3 apples. "
        "6 divided by 2 equals 3!"
    )
}

API_BASE_URL = "http://localhost:8000/api/v1"
USER_ID = "test-user-illustration"

def build_structured_prompt(video_data):
    """Build a structured prompt for video generation"""
    
    topic = video_data["topic"]
    title = video_data["title"]
    content = video_data["content"]
    visual_description = video_data["visual_description"]
    equation = video_data["equation"]
    narration = NARRATION_TEXTS[topic]
    
    # Combine all sections into a comprehensive prompt
    prompt = (
        f"{PROMPT_SECTIONS['design']} "
        f"The video should teach about: {title}. "
        f"Specifically, it should demonstrate: {content}. "
        f"Visual sequence: {visual_description}. "
        f"Display the equation '{equation}' clearly on screen. "
        f"{PROMPT_SECTIONS['instructor_voice']} "
        f"The exact narration should be: \"{narration}\" "
        f"The animation should be smooth, colorful, and engaging for young learners. "
        f"Focus on clear visual storytelling without any instructor on screen. "
        f"Make sure the visual elements clearly support and illustrate the narration. "
        f"Use consistent apple imagery and colors throughout the animation."
    )
    
    return prompt

async def generate_illustration_video(video_data, index):
    """Generate a single illustration-focused video"""
    
    topic = video_data["topic"]
    title = video_data["title"]
    
    print(f"🎬 Starting video {index + 1}/5: {title}")
    print(f"📋 Topic: {topic}")
    print(f"🎯 Focus: Illustration-only (no instructor)")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Build structured prompt
        prompt = build_structured_prompt(video_data)
        
        print(f"📝 Generated structured prompt:")
        print(f"   Design: {PROMPT_SECTIONS['design'][:50]}...")
        print(f"   Voice: {PROMPT_SECTIONS['instructor_voice'][:50]}...")
        print(f"   Narration: {NARRATION_TEXTS[topic][:50]}...")
        print("-" * 60)
        
        # Send video generation request
        response = requests.post(
            f"{API_BASE_URL}/chat/message",
            headers={
                "Content-Type": "application/json",
                "X-User-ID": USER_ID
            },
            json={
                "message": {
                    "id": f"msg-{topic}",
                    "userId": USER_ID,
                    "content": f"Create an illustration-focused video teaching {title.lower()}",
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
        generated_prompt = data["responses"][0]["video"]["prompt"]
        
        print(f"✅ Video {index + 1} generation started: {video_id}")
        print(f"📝 AI Generated prompt:")
        print(f"   {generated_prompt}")
        print("-" * 60)
        
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
                    
                    video_filename = f"illustration_{index + 1}_{topic}_{video_id}.mp4"
                    video_path = downloads_dir / video_filename
                    
                    with open(video_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"💾 Video {index + 1} downloaded: {video_path}")
                    print(f"📊 File size: {video_path.stat().st_size:,} bytes")
                    
                    return {
                        "index": index + 1,
                        "topic": topic,
                        "title": title,
                        "video_id": video_id,
                        "generation_time": generation_time,
                        "total_time": total_time,
                        "file_path": str(video_path),
                        "file_size": video_path.stat().st_size,
                        "prompt": generated_prompt
                    }
                else:
                    print(f"❌ Error downloading video {index + 1}")
                    return None
                    
            elif video_status == "failed":
                error_info = status_data["video"].get("error", {})
                print(f"❌ Video {index + 1} generation failed")
                print(f"   Error: {error_info.get('message', 'Unknown error')}")
                return None
                
    except Exception as e:
        print(f"❌ Error with video {index + 1}: {str(e)}")
        return None

async def main():
    """Main test function"""
    print("🚀 Starting Math Operations Series - 4 illustration-focused videos")
    print("🎯 Goal: Test consistency across related math operation videos")
    print("📚 Series: Addition → Subtraction → Multiplication → Division")
    print("⏱️  Duration: 8 seconds each")
    print("🎨 Style: Illustration-focused with structured prompts")
    print("👩 Voice: Female narrator (non-visual)")
    print("🍎 Visual: Consistent apple imagery throughout series")
    print()
    
    start_time = time.time()
    results = []
    
    # Generate videos sequentially
    for i, video_data in enumerate(VIDEO_TOPICS):
        result = await generate_illustration_video(video_data, i)
        if result:
            results.append(result)
        
        # Small delay between requests
        if i < len(VIDEO_TOPICS) - 1:
            print("⏳ Waiting 5 seconds before next video...")
            await asyncio.sleep(5)
    
    total_time = time.time() - start_time
    
    # Print comprehensive summary
    print("\n" + "="*80)
    print("📊 MATH OPERATIONS SERIES SUMMARY")
    print("="*80)
    print(f"✅ Videos generated: {len(results)}/{len(VIDEO_TOPICS)}")
    print(f"⏱️  Total test time: {total_time:.2f} seconds")
    print(f"📁 Videos saved to: downloads/")
    print(f"🎯 Series focus: Consistency testing across math operations")
    
    if results:
        print("\n📋 Individual Results:")
        for result in results:
            print(f"  {result['index']}. {result['title']}")
            print(f"     Topic: {result['topic']}")
            print(f"     Generation: {result['generation_time']:.2f}s")
            print(f"     File: {result['file_path']}")
            print(f"     Size: {result['file_size']:,} bytes")
            print()
        
        avg_generation_time = sum(r['generation_time'] for r in results) / len(results)
        total_file_size = sum(r['file_size'] for r in results)
        
        print(f"📈 Statistics:")
        print(f"   Average generation time: {avg_generation_time:.2f} seconds")
        print(f"   Total file size: {total_file_size:,} bytes")
        print(f"   Average file size: {total_file_size // len(results):,} bytes")
        
        print(f"\n🎯 Prompt Structure Used:")
        print(f"   Design Section: {PROMPT_SECTIONS['design'][:60]}...")
        print(f"   Voice Section: {PROMPT_SECTIONS['instructor_voice'][:60]}...")
    
    print("\n🎉 Math Operations Series video generation test completed!")
    print("🔍 Check videos for visual and narrative consistency across the series!")

if __name__ == "__main__":
    asyncio.run(main())
