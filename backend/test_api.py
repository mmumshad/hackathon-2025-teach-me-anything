#!/usr/bin/env python3
"""
Test script for TechMeAnything API
Tests both regular chat and quiz generation
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_chat_message(message, require_audio=False):
    """Test chat message endpoint"""
    print(f"💬 Testing Chat Message: '{message}'")
    
    payload = {
        "message": {
            "id": "test-msg-1",
            "userId": "test-user-123",
            "content": message,
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "requireAudio": require_audio
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-user-123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            headers=headers,
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response Content: {data['responses'][0]['content'][:200]}...")
            if data['responses'][0].get('quiz'):
                print(f"Quiz Generated: {len(data['responses'][0]['quiz'])} questions")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    print()

def main():
    """Run all tests"""
    print("🚀 Starting TechMeAnything API Tests\n")
    
    # Test health endpoint
    test_health()
    
    # Test regular chat
    test_chat_message("Tell me about photosynthesis")
    
    # Test quiz generation
    test_chat_message("Can you create a quiz about the solar system?")
    
    # Test audio request
    test_chat_message("Explain gravity to a 5th grader", require_audio=True)
    
    print("✅ Tests completed!")

if __name__ == "__main__":
    main()
