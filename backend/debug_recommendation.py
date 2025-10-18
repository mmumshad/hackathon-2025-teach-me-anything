#!/usr/bin/env python3
"""
Debug script to test recommendation logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.supabase_mcp_service import SupabaseMCPService

def debug_recommendation_logic():
    """Debug the recommendation logic step by step"""
    
    print("🔍 Debugging Recommendation Logic")
    print("=" * 50)
    
    # Test message
    message = "could you please recommend me book on Physics"
    print(f"Test message: '{message}'")
    
    # Test 1: Check material request detection
    print("\n1️⃣ Testing Material Request Detection...")
    keywords = ["book", "recommend", "study material", "resource", "learn", "read", "watch", "course"]
    is_material_request = any(keyword in message.lower() for keyword in keywords)
    print(f"Keywords found: {[kw for kw in keywords if kw in message.lower()]}")
    print(f"Is material request: {is_material_request}")
    
    # Test 2: Check Supabase service
    print("\n2️⃣ Testing Supabase Service...")
    supabase_service = SupabaseMCPService()
    is_available = supabase_service.is_available()
    print(f"Supabase service available: {is_available}")
    
    if is_available:
        # Test 3: Check subject extraction
        print("\n3️⃣ Testing Subject Extraction...")
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
        
        print(f"Extracted subject: {subject}")
        
        # Test 4: Check study materials retrieval
        if subject:
            print(f"\n4️⃣ Testing Study Materials Retrieval for {subject}...")
            try:
                materials = supabase_service.get_study_recommendations(
                    subject=subject,
                    grade_level="middle",  # Default grade level
                    limit=3
                )
                print(f"Materials retrieved: {len(materials) if materials else 0}")
                if materials:
                    for i, material in enumerate(materials, 1):
                        print(f"   {i}. {material.get('title', 'Unknown')} by {material.get('author', 'Unknown')}")
                else:
                    print("   No materials found")
            except Exception as e:
                print(f"   Error retrieving materials: {e}")
    
    # Test 5: Check the full logic
    print(f"\n5️⃣ Full Logic Check...")
    print(f"   is_material_request: {is_material_request}")
    print(f"   supabase_available: {is_available}")
    print(f"   should_use_supabase: {is_material_request and is_available}")

if __name__ == "__main__":
    debug_recommendation_logic()
