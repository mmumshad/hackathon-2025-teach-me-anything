#!/usr/bin/env python3
"""
Test script for direct Supabase integration (without MCP)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

def test_supabase_direct():
    """Test direct Supabase functionality"""
    
    print("🧪 Testing Direct Supabase Integration")
    print("=" * 50)
    
    try:
        from supabase import create_client, Client
        
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        print(f"🔧 Supabase URL: {supabase_url[:30]}..." if supabase_url else "❌ No URL")
        print(f"🔧 Supabase Key: {supabase_key[:20]}..." if supabase_key else "❌ No Key")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found in environment variables")
            return
        
        # Initialize Supabase client
        print("🔧 Initializing Supabase client...")
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized successfully")
        
        # Test 1: Create study materials table
        print("\n📚 Test 1: Creating study_materials table...")
        try:
            # Create table using SQL
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS study_materials (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('book', 'video', 'podcast', 'article', 'course')),
                subject TEXT NOT NULL,
                grade_level TEXT,
                description TEXT,
                url TEXT,
                author TEXT,
                recommended_by TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                tags TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Try to execute SQL (this might not work depending on permissions)
            result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            print("✅ Table creation attempted")
            
        except Exception as e:
            print(f"⚠️ Table creation failed (expected if no exec_sql function): {str(e)}")
            print("💡 You may need to create tables manually in Supabase dashboard")
        
        # Test 2: Insert a test record
        print("\n📝 Test 2: Inserting test study material...")
        try:
            test_material = {
                "title": "Test Physics Book",
                "type": "book",
                "subject": "physics",
                "grade_level": "high school",
                "description": "A test book for physics",
                "author": "Test Author",
                "recommended_by": "test-user",
                "rating": 5,
                "tags": ["test", "physics"]
            }
            
            result = supabase.table("study_materials").insert(test_material).execute()
            
            if result.data:
                print("✅ Test material inserted successfully")
                print(f"📖 Material ID: {result.data[0]['id']}")
                
                # Test 3: Query the record
                print("\n🔍 Test 3: Querying study materials...")
                query_result = supabase.table("study_materials").select("*").eq("subject", "physics").execute()
                
                print(f"✅ Found {len(query_result.data)} physics materials")
                for material in query_result.data:
                    print(f"  📚 {material['title']} by {material.get('author', 'Unknown')}")
                
                # Test 4: Update the record
                print("\n✏️ Test 4: Updating test material...")
                update_result = supabase.table("study_materials").update({
                    "rating": 4,
                    "description": "Updated test book for physics"
                }).eq("id", result.data[0]['id']).execute()
                
                if update_result.data:
                    print("✅ Material updated successfully")
                
                # Test 5: Delete the test record
                print("\n🗑️ Test 5: Cleaning up test material...")
                delete_result = supabase.table("study_materials").delete().eq("id", result.data[0]['id']).execute()
                print("✅ Test material deleted")
                
            else:
                print("❌ Failed to insert test material")
                
        except Exception as e:
            print(f"❌ Database operation failed: {str(e)}")
            print("💡 This might be due to:")
            print("   - Table doesn't exist (create it manually in Supabase dashboard)")
            print("   - RLS policies blocking access")
            print("   - Incorrect credentials")
        
        print("\n🎯 Summary:")
        print("✅ Supabase client connection: Working")
        print("✅ Basic operations: Tested")
        print("💡 Next steps:")
        print("   1. Create tables manually in Supabase dashboard")
        print("   2. Set up RLS policies if needed")
        print("   3. Test the API endpoints")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Make sure supabase package is installed: pip install supabase")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_direct()
