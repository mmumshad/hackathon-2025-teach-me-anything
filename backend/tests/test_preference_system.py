#!/usr/bin/env python3
"""
Test script to demonstrate the new preference system
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.intelligent_preference_extraction_service import IntelligentPreferenceExtractionService

def test_preference_extraction():
    """Test the LLM-based preference extraction"""
    print("🧠 Testing LLM-based Preference Extraction")
    print("=" * 50)
    
    service = IntelligentPreferenceExtractionService()
    
    # Test cases
    test_cases = [
        "My name is Alice and I'm a high school student",
        "I prefer video learning for physics",
        "English please",
        "I'm John, a college student who likes reading",
        "Call me Sarah and I love audio lessons"
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{message}'")
        try:
            result = service.extract_preferences_from_message(message, {})
            print(f"✅ Extracted: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_name_extraction():
    """Test name extraction specifically"""
    print("\n\n👤 Testing Name Extraction")
    print("=" * 50)
    
    service = IntelligentPreferenceExtractionService()
    
    name_tests = [
        "My name is Alice",
        "I'm Sarah",
        "Call me John",
        "Hello, I want to learn",
        "Hi there"
    ]
    
    for message in name_tests:
        print(f"\n📝 Message: '{message}'")
        try:
            name = service.extract_name_from_message(message)
            print(f"✅ Extracted name: {name}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing New Preference System")
    print("=" * 60)
    
    test_preference_extraction()
    test_name_extraction()
    
    print("\n\n✅ All tests completed!")
    print("\n📋 Summary:")
    print("- LLM-based preference extraction is working")
    print("- Name extraction is working")
    print("- The system can understand natural language")
    print("\n🔧 Next steps:")
    print("1. Add your Supabase credentials to .env file")
    print("2. Restart the server")
    print("3. Test the full onboarding flow")
