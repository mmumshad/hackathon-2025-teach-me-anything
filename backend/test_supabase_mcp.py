#!/usr/bin/env python3
"""
Test script for Supabase MCP integration
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def test_supabase_mcp():
    """Test the Supabase MCP service"""
    try:
        from services.supabase_mcp_service import SupabaseMCPService
        
        print("🔧 Initializing Supabase MCP Service...")
        service = SupabaseMCPService()
        
        print(f"✅ Supabase available: {service.is_available()}")
        
        if service.is_available():
            print("🔍 Testing MCP tools...")
            tools = await service.list_available_tools()
            print(f"📋 Available tools: {tools}")
            
            if tools:
                print("🔍 Testing documentation search...")
                docs = await service.search_docs("database setup", limit=3)
                print(f"📚 Found {len(docs)} documentation results")
                for doc in docs[:2]:  # Show first 2 results
                    print(f"  - {doc.get('title', 'No title')}")
            
            print("🏗️ Testing knowledge graph table creation...")
            success = service.create_knowledge_graph_tables()
            print(f"✅ Tables created: {success}")
            
            if success:
                print("📚 Testing study material addition...")
                result = service.add_study_material(
                    title="Introduction to Physics",
                    material_type="book",
                    subject="physics",
                    recommended_by="test-user",
                    description="A great book for learning physics basics",
                    author="Dr. Physics",
                    grade_level="high school",
                    rating=5,
                    tags=["beginner", "fundamentals"]
                )
                print(f"✅ Material added: {result['success']}")
                if result['success']:
                    print(f"📖 Material ID: {result['material']['id']}")
                
                print("🔍 Testing study material retrieval...")
                materials = service.get_study_recommendations(
                    subject="physics",
                    grade_level="high school",
                    limit=5
                )
                print(f"📚 Found {len(materials)} physics materials")
                for material in materials:
                    print(f"  - {material['title']} by {material.get('author', 'Unknown')}")
        
        print("🧹 Cleaning up...")
        await service.close_mcp_session()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supabase_mcp())
