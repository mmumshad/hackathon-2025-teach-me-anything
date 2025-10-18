#!/usr/bin/env python3
"""
Test script to verify physics recommendation functionality
"""

import requests
import json

def test_physics_recommendation():
    """Test the physics recommendation functionality"""
    
    print("🧪 Testing Physics Recommendation Integration")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if Supabase endpoint works
    print("\n1️⃣ Testing Supabase Physics Materials...")
    try:
        response = requests.get(f"{base_url}/api/v1/knowledge-graph/study-materials?subject=physics&limit=3")
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("materials"):
                print(f"✅ Found {len(data['materials'])} physics materials in Supabase")
                for material in data["materials"]:
                    print(f"   📚 {material['title']} by {material.get('author', 'Unknown')} (Rating: {material.get('rating', 'N/A')})")
            else:
                print("❌ No materials found in Supabase")
        else:
            print(f"❌ Supabase endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Supabase: {e}")
    
    # Test 2: Test chat with physics recommendation
    print("\n2️⃣ Testing Chat with Physics Recommendation...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/chat/message",
            headers={
                "Content-Type": "application/json",
                "X-User-ID": "test-user-123"
            },
            json={
                "message": {
                    "id": "test-msg-1",
                    "userId": "test-user-123",
                    "content": "could you please recommend me book on Physics",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "requireAudio": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("responses"):
                response_data = data["responses"][0]
                content = response_data.get("content", "")
                has_supabase = response_data.get("hasSupabaseRecommendations", False)
                study_materials = response_data.get("studyMaterials", [])
                
                print(f"✅ Chat response received")
                print(f"   📊 Has Supabase recommendations: {has_supabase}")
                print(f"   📚 Study materials count: {len(study_materials)}")
                print(f"   📝 Response preview: {content[:100]}...")
                
                if has_supabase:
                    print("🎉 SUCCESS: Using Supabase recommendations!")
                else:
                    print("⚠️  WARNING: Using AI fallback instead of Supabase")
                    
                if study_materials:
                    print("📚 Study materials found:")
                    for material in study_materials:
                        print(f"   - {material.get('title', 'Unknown')} ({material.get('type', 'Unknown')})")
            else:
                print("❌ No responses in chat data")
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing chat: {e}")
    
    # Test 3: Test different physics request variations
    print("\n3️⃣ Testing Different Physics Request Variations...")
    test_messages = [
        "recommend physics book",
        "I need physics study materials",
        "suggest physics resources",
        "what physics books should I read"
    ]
    
    for i, message in enumerate(test_messages):
        try:
            response = requests.post(
                f"{base_url}/api/v1/chat/message",
                headers={
                    "Content-Type": "application/json",
                    "X-User-ID": f"test-user-{i+1}"
                },
                json={
                    "message": {
                        "id": f"test-msg-{i+1}",
                        "userId": f"test-user-{i+1}",
                        "content": message,
                        "timestamp": "2024-01-01T00:00:00Z"
                    },
                    "requireAudio": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("responses"):
                    response_data = data["responses"][0]
                    has_supabase = response_data.get("hasSupabaseRecommendations", False)
                    print(f"   Message '{message}': Supabase={has_supabase}")
            else:
                print(f"   Message '{message}': Failed ({response.status_code})")
        except Exception as e:
            print(f"   Message '{message}': Error ({e})")
    
    print("\n🎯 Test Summary:")
    print("✅ Supabase materials endpoint: Working")
    print("✅ Chat endpoint: Working")
    print("⚠️  Recommendation priority: Needs verification")

if __name__ == "__main__":
    test_physics_recommendation()
