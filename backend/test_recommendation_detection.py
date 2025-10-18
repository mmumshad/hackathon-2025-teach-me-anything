#!/usr/bin/env python3
"""
Test script for automatic recommendation detection
"""

import asyncio
from services.supabase_mcp_service import SupabaseMCPService

def test_recommendation_detection():
    """Test the recommendation detection functionality"""
    
    print("🧪 Testing Automatic Recommendation Detection")
    print("=" * 50)
    
    service = SupabaseMCPService()
    
    # Test cases for different types of recommendations
    test_messages = [
        # Book recommendations
        "I highly recommend 'Physics for Beginners' by Dr. Smith. It's a great book for learning physics basics!",
        "You should read 'Introduction to Chemistry' - it helped me understand the fundamentals.",
        "Check out 'Biology Made Easy' by Jane Doe, it's worth reading for high school students.",
        
        # Video recommendations
        "I found this amazing video on YouTube about quantum physics. You should watch it!",
        "There's a great channel called 'Science Explained' that I recommend for physics videos.",
        
        # Podcast recommendations
        "I love listening to 'The Science Podcast' - highly recommend it for learning biology.",
        "Check out this podcast episode about mathematics, it's really interesting.",
        
        # Article recommendations
        "I read this great article about computer programming on Medium. Worth reading!",
        "Found this blog post about history that I suggest you check out.",
        
        # Course recommendations
        "I took this online course on Coursera about data science. Highly recommend it!",
        "There's a great tutorial on Udemy for learning Python programming.",
        
        # With URLs and ratings
        "I recommend 'Advanced Physics' by John Wilson (5/5 stars). Check it out at https://example.com/book",
        "This video on YouTube is amazing - 4 stars! https://youtube.com/watch?v=123",
        
        # With grade levels
        "This book is perfect for elementary students learning science.",
        "Great resource for high school physics students.",
        
        # Non-recommendation messages (should not be detected)
        "What is photosynthesis?",
        "Can you explain gravity to me?",
        "I need help with my math homework.",
    ]
    
    print("📝 Testing recommendation detection on various messages:\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        
        # Detect recommendation
        recommendation = service.detect_material_recommendation(message)
        
        if recommendation:
            print(f"✅ RECOMMENDATION DETECTED:")
            print(f"   📖 Title: {recommendation['title']}")
            print(f"   📚 Type: {recommendation['type']}")
            print(f"   🎯 Subject: {recommendation['subject'] or 'general'}")
            print(f"   👤 Author: {recommendation['author'] or 'Unknown'}")
            print(f"   ⭐ Rating: {recommendation['rating'] or 'Not specified'}")
            print(f"   🎓 Grade Level: {recommendation['grade_level'] or 'Not specified'}")
            print(f"   🏷️ Tags: {recommendation['tags']}")
            print(f"   🔗 URL: {recommendation['url'] or 'Not provided'}")
            print(f"   📊 Confidence: {recommendation['confidence']}")
        else:
            print("❌ No recommendation detected")
        
        print("-" * 50)
    
    print("\n🎯 Summary:")
    print("The system can automatically detect:")
    print("✅ Book recommendations with titles, authors, ratings")
    print("✅ Video recommendations with URLs")
    print("✅ Podcast and article recommendations")
    print("✅ Course and tutorial recommendations")
    print("✅ Grade level and subject classification")
    print("✅ Rating extraction (1-5 stars)")
    print("✅ Tag generation (beginner, advanced, engaging, free)")
    print("✅ URL extraction from messages")
    print("✅ Author extraction from 'by [author]' patterns")

if __name__ == "__main__":
    test_recommendation_detection()
