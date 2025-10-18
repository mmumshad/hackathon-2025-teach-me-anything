#!/usr/bin/env python3
"""
Test script for Supabase user preferences and intelligent preference extraction
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test-user-supabase-prefs"

def test_preference_extraction():
    """Test intelligent preference extraction from messages"""
    print("🧠 Testing Intelligent Preference Extraction...")
    
    test_messages = [
        "Hi, my name is Alice and I'm in high school. I prefer video learning for physics.",
        "I'm John, a college student. I like reading books about mathematics.",
        "Call me Sarah. I'm in middle school and I love audio content for learning history.",
        "I'm an adult learner interested in computer science. I prefer interactive learning.",
        "Hello! I want to learn about chemistry. I'm in 10th grade."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        
        # Send chat message
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            data={
                "message": message,
                "message_id": f"test-msg-{i}",
                "user_id": f"{TEST_USER_ID}-{i}",
                "timestamp": "2024-01-01T00:00:00Z",
                "require_audio": False
            },
            headers={"X-User-ID": f"{TEST_USER_ID}-{i}"}
        )
        
        if response.status_code == 200:
            print("✅ Message processed successfully")
            
            # Get user preferences to see what was extracted
            pref_response = requests.get(
                f"{BASE_URL}/api/v1/user/preferences",
                headers={"X-User-ID": f"{TEST_USER_ID}-{i}"}
            )
            
            if pref_response.status_code == 200:
                preferences = pref_response.json()["preferences"]
                print(f"📊 Extracted preferences: {json.dumps(preferences, indent=2)}")
            else:
                print(f"❌ Failed to get preferences: {pref_response.status_code}")
        else:
            print(f"❌ Failed to process message: {response.status_code}")
            print(f"Response: {response.text}")

def test_preference_storage():
    """Test Supabase preference storage and retrieval"""
    print("\n🗄️ Testing Supabase Preference Storage...")
    
    test_preferences = {
        "name": "TestUser",
        "grade_level": "high",
        "language": "en",
        "learning_style": "video",
        "preferred_subjects": ["physics", "mathematics"]
    }
    
    # Store preferences
    print("💾 Storing preferences...")
    response = requests.post(
        f"{BASE_URL}/api/v1/user/preferences",
        json=test_preferences,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    if response.status_code == 200:
        print("✅ Preferences stored successfully")
        
        # Retrieve preferences
        print("📥 Retrieving preferences...")
        response = requests.get(
            f"{BASE_URL}/api/v1/user/preferences",
            headers={"X-User-ID": TEST_USER_ID}
        )
        
        if response.status_code == 200:
            retrieved_prefs = response.json()["preferences"]
            print(f"📊 Retrieved preferences: {json.dumps(retrieved_prefs, indent=2)}")
            
            # Verify they match
            if retrieved_prefs == test_preferences:
                print("✅ Preferences match perfectly!")
            else:
                print("⚠️ Preferences don't match exactly")
        else:
            print(f"❌ Failed to retrieve preferences: {response.status_code}")
    else:
        print(f"❌ Failed to store preferences: {response.status_code}")
        print(f"Response: {response.text}")

def test_user_context():
    """Test user context endpoint"""
    print("\n👤 Testing User Context...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/user/context",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    if response.status_code == 200:
        context = response.json()["context"]
        print(f"📊 User context: {json.dumps(context, indent=2)}")
        print("✅ User context retrieved successfully")
    else:
        print(f"❌ Failed to get user context: {response.status_code}")

def test_video_audio_generation():
    """Test video and audio generation based on preferences"""
    print("\n🎬 Testing Video/Audio Generation Logic...")
    
    # Test with video preference user
    video_user = f"{TEST_USER_ID}-video"
    
    # Set video preferences
    video_prefs = {
        "name": "VideoUser",
        "grade_level": "high",
        "language": "en",
        "learning_style": "video"
    }
    
    requests.post(
        f"{BASE_URL}/api/v1/user/preferences",
        json=video_prefs,
        headers={"X-User-ID": video_user}
    )
    
    # Send message that should trigger video generation
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        data={
            "message": "Can you explain quantum physics?",
            "message_id": "video-test-msg",
            "user_id": video_user,
            "timestamp": "2024-01-01T00:00:00Z",
            "require_audio": False
        },
        headers={"X-User-ID": video_user}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("response", {}).get("video"):
            print("✅ Video generation triggered correctly")
        else:
            print("⚠️ Video generation not triggered")
    else:
        print(f"❌ Failed to test video generation: {response.status_code}")

def main():
    """Run all tests"""
    print("🚀 Starting Supabase Preferences and Intelligent Extraction Tests")
    print("=" * 70)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Server is not running. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_preference_storage()
    test_preference_extraction()
    test_user_context()
    test_video_audio_generation()
    
    print("\n" + "=" * 70)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()
