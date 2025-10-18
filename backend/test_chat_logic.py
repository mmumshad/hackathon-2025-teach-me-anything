#!/usr/bin/env python3
"""
Test the chat logic directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.supabase_mcp_service import SupabaseMCPService

def test_chat_logic():
    """Test the chat logic step by step"""
    
    print("🧪 Testing Chat Logic Step by Step")
    print("=" * 50)
    
    # Test message
    message = "could you please recommend me book on Physics"
    print(f"Test message: '{message}'")
    
    # Initialize services
    supabase_service = SupabaseMCPService()
    
    # Step 1: Check material request detection
    print("\n1️⃣ Material Request Detection:")
    keywords = ["book", "recommend", "study material", "resource", "learn", "read", "watch", "course"]
    is_material_request = any(keyword in message.lower() for keyword in keywords)
    found_keywords = [kw for kw in keywords if kw in message.lower()]
    print(f"   Keywords found: {found_keywords}")
    print(f"   Is material request: {is_material_request}")
    
    # Step 2: Check Supabase availability
    print("\n2️⃣ Supabase Service:")
    is_available = supabase_service.is_available()
    print(f"   Supabase available: {is_available}")
    
    # Step 3: Subject extraction
    print("\n3️⃣ Subject Extraction:")
    message_lower = message.lower()
    subject = None
    if "physics" in message_lower:
        subject = "physics"
    elif "chemistry" in message_lower:
        subject = "chemistry"
    elif "biology" in message_lower:
        subject = "biology"
    elif "math" in message_lower:
        subject = "mathematics"
    elif "history" in message_lower:
        subject = "history"
    print(f"   Extracted subject: {subject}")
    
    # Step 4: Get study materials
    print("\n4️⃣ Study Materials Retrieval:")
    study_materials = []
    has_supabase_recommendations = False
    
    if is_material_request and is_available and subject:
        print(f"   ✅ All conditions met - checking Supabase for {subject}")
        
        grade_level = "middle"  # Default grade level
        
        # First try with specific grade level
        study_materials = supabase_service.get_study_recommendations(
            subject=subject,
            grade_level=grade_level,
            limit=3
        )
        print(f"   Materials with grade filter ({grade_level}): {len(study_materials) if study_materials else 0}")
        
        # If no materials found with specific grade level, try without grade filter
        if not study_materials or len(study_materials) == 0:
            print(f"   No materials found for {subject} at {grade_level} level, trying without grade filter")
            study_materials = supabase_service.get_study_recommendations(
                subject=subject,
                grade_level=None,  # No grade level filter
                limit=3
            )
            print(f"   Materials without grade filter: {len(study_materials) if study_materials else 0}")
        
        # Check if we found recommendations
        if study_materials and len(study_materials) > 0:
            has_supabase_recommendations = True
            print(f"   ✅ Found {len(study_materials)} Supabase recommendations!")
            
            # Show the materials
            for i, material in enumerate(study_materials, 1):
                print(f"      {i}. {material.get('title')} by {material.get('author')} (Rating: {material.get('rating')}/5)")
        else:
            print(f"   ❌ No Supabase recommendations found")
    else:
        print(f"   ❌ Conditions not met:")
        print(f"      - is_material_request: {is_material_request}")
        print(f"      - is_available: {is_available}")
        print(f"      - subject: {subject}")
    
    # Step 5: Final result
    print(f"\n5️⃣ Final Result:")
    print(f"   Has Supabase recommendations: {has_supabase_recommendations}")
    print(f"   Study materials count: {len(study_materials) if study_materials else 0}")
    print(f"   Response type: {'Supabase' if has_supabase_recommendations else 'AI Fallback'}")

if __name__ == "__main__":
    test_chat_logic()
