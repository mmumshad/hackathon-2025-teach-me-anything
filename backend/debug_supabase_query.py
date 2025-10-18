#!/usr/bin/env python3
"""
Debug script to test Supabase query directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.supabase_mcp_service import SupabaseMCPService

def debug_supabase_query():
    """Debug the Supabase query directly"""
    
    print("🔍 Debugging Supabase Query")
    print("=" * 40)
    
    supabase_service = SupabaseMCPService()
    
    if not supabase_service.is_available():
        print("❌ Supabase service not available")
        return
    
    print("✅ Supabase service available")
    
    # Test 1: Query without grade level filter
    print("\n1️⃣ Testing query without grade level filter...")
    try:
        materials = supabase_service.get_study_recommendations(
            subject="physics",
            grade_level=None,  # No grade level filter
            limit=5
        )
        print(f"Materials found (no grade filter): {len(materials)}")
        for material in materials:
            print(f"   - {material.get('title')} (Grade: {material.get('grade_level', 'None')})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Query with grade level filter
    print("\n2️⃣ Testing query with grade level filter...")
    try:
        materials = supabase_service.get_study_recommendations(
            subject="physics",
            grade_level="middle",  # With grade level filter
            limit=5
        )
        print(f"Materials found (with grade filter): {len(materials)}")
        for material in materials:
            print(f"   - {material.get('title')} (Grade: {material.get('grade_level', 'None')})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Query with high school grade level
    print("\n3️⃣ Testing query with high school grade level...")
    try:
        materials = supabase_service.get_study_recommendations(
            subject="physics",
            grade_level="high school",  # With high school filter
            limit=5
        )
        print(f"Materials found (high school filter): {len(materials)}")
        for material in materials:
            print(f"   - {material.get('title')} (Grade: {material.get('grade_level', 'None')})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Direct Supabase query
    print("\n4️⃣ Testing direct Supabase query...")
    try:
        result = supabase_service.supabase.table("study_materials").select("*").eq("subject", "physics").execute()
        print(f"Direct query result: {len(result.data)} materials")
        for material in result.data:
            print(f"   - {material.get('title')} (Grade: {material.get('grade_level', 'None')})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_supabase_query()
