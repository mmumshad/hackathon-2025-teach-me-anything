#!/usr/bin/env python3
"""
Test the updated recommendation logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_mcp_service import SupabaseMCPService

def test_updated_logic():
    """Test the updated recommendation logic"""
    
    print("🧪 Testing Updated Recommendation Logic")
    print("=" * 50)
    
    # Test message
    message = "could you please recommend me book on Physics"
    print(f"Test message: '{message}'")
    
    # Initialize services
    supabase_service = SupabaseMCPService()
    
    # Check if user is asking for study material recommendations
    is_material_request = any(keyword in message.lower() for keyword in [
        "book", "recommend", "study material", "resource", "learn", "read", "watch", "course"
    ])
    print(f"Is material request: {is_material_request}")
    
    # Check for Supabase recommendations first if this is a material request
    study_materials = []
    has_supabase_recommendations = False
    ai_response = ""
    
    if is_material_request and supabase_service.is_available():
        print("✅ Material request detected and Supabase available")
        
        # Extract subject from the message
        subject = None
        message_lower = message.lower()
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
        
        if subject:
            grade_level = "middle"  # Default grade level
            
            # First try with specific grade level
            study_materials = supabase_service.get_study_recommendations(
                subject=subject,
                grade_level=grade_level,
                limit=3
            )
            print(f"Materials with grade filter ({grade_level}): {len(study_materials) if study_materials else 0}")
            
            # If no materials found with specific grade level, try without grade filter
            if not study_materials or len(study_materials) == 0:
                print(f"No materials found for {subject} at {grade_level} level, trying without grade filter")
                study_materials = supabase_service.get_study_recommendations(
                    subject=subject,
                    grade_level=None,  # No grade level filter
                    limit=3
                )
                print(f"Materials without grade filter: {len(study_materials) if study_materials else 0}")
            
            # Check if we found recommendations in Supabase
            if study_materials and len(study_materials) > 0:
                has_supabase_recommendations = True
                print(f"✅ Found {len(study_materials)} Supabase recommendations for {subject}")
                
                # Generate a personalized response based on Supabase recommendations
                ai_response = f"Great question! Based on our community recommendations, here are some excellent {subject} resources that other students have found helpful:\n\n"
                
                for i, material in enumerate(study_materials, 1):
                    rating_stars = "⭐" * (material.get('rating', 0))
                    grade_info = f" (Grade: {material.get('grade_level', 'All levels')})" if material.get('grade_level') else ""
                    author_info = f" by {material.get('author', 'Unknown')}" if material.get('author') else ""
                    url_info = f"\n🔗 Link: {material.get('url')}" if material.get('url') else ""
                    tags_info = f"\n🏷️ Tags: {', '.join(material.get('tags', []))}" if material.get('tags') else ""
                    
                    ai_response += f"{i}. **{material.get('title', 'Unknown Title')}**{author_info}{grade_info}\n"
                    ai_response += f"   📚 Type: {material.get('type', 'Unknown').title()}\n"
                    ai_response += f"   ⭐ Rating: {rating_stars} ({material.get('rating', 'N/A')}/5)\n"
                    ai_response += f"   📝 Description: {material.get('description', 'No description available')}{url_info}{tags_info}\n\n"
                
                ai_response += f"These recommendations come from our community of learners who have found these resources helpful for studying {subject}. "
                ai_response += f"Feel free to ask about any specific topic within {subject} or if you'd like more recommendations!"
                
            else:
                print(f"❌ No Supabase recommendations found for {subject}, using AI fallback")
    
    # Generate AI response only if we don't have Supabase recommendations
    if not has_supabase_recommendations:
        print("🔄 Generating AI fallback response...")
        ai_response = "AI-generated response would go here..."
    
    print(f"\n🎯 Results:")
    print(f"   Has Supabase recommendations: {has_supabase_recommendations}")
    print(f"   Study materials count: {len(study_materials) if study_materials else 0}")
    print(f"   Response type: {'Supabase' if has_supabase_recommendations else 'AI'}")
    
    if has_supabase_recommendations:
        print(f"\n📝 Supabase Response Preview:")
        print(ai_response[:200] + "...")

if __name__ == "__main__":
    test_updated_logic()
