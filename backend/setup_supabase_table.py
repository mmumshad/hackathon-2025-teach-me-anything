#!/usr/bin/env python3
"""
Setup script to create the user_preferences table in Supabase
"""

import os
from supabase import create_client, Client

def setup_supabase_table():
    """Create the user_preferences table in Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # SQL to create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_preferences (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255),
            grade_level VARCHAR(50),
            language VARCHAR(10) DEFAULT 'en',
            learning_style VARCHAR(50) DEFAULT 'reading',
            preferred_subjects TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create index
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
        """
        
        # Create function for updating timestamp
        create_function_sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
        
        # Create trigger
        create_trigger_sql = """
        DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
        CREATE TRIGGER update_user_preferences_updated_at 
            BEFORE UPDATE ON user_preferences 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        print("📝 Creating user_preferences table...")
        
        # Execute SQL statements
        try:
            # Note: These operations might need to be done through Supabase dashboard
            # as the Python client doesn't support DDL operations directly
            print("⚠️  Note: Please run the following SQL in your Supabase dashboard:")
            print("\n" + "="*50)
            print(create_table_sql)
            print(create_index_sql)
            print(create_function_sql)
            print(create_trigger_sql)
            print("="*50)
            
            # Test the connection by trying to query the table
            print("\n🔍 Testing table access...")
            result = supabase.table("user_preferences").select("*").limit(1).execute()
            print("✅ Table access successful")
            
            return True
            
        except Exception as e:
            if "relation \"user_preferences\" does not exist" in str(e):
                print("❌ Table doesn't exist yet. Please create it using the SQL above.")
                return False
            else:
                print(f"❌ Error testing table: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def test_preferences_service():
    """Test the preferences service"""
    try:
        from services.supabase_user_preferences_service import SupabaseUserPreferencesService
        
        print("\n🧪 Testing SupabaseUserPreferencesService...")
        service = SupabaseUserPreferencesService()
        
        if service.client is None:
            print("❌ Service initialization failed")
            return False
        
        # Test getting default preferences
        test_user_id = "test-setup-user"
        preferences = service.get_user_preferences(test_user_id)
        print(f"✅ Default preferences: {preferences}")
        
        # Test storing preferences
        test_prefs = {
            "name": "TestUser",
            "grade_level": "high",
            "language": "en",
            "learning_style": "video"
        }
        
        success = service.store_user_preferences(test_user_id, test_prefs)
        if success:
            print("✅ Preference storage successful")
            
            # Test retrieval
            retrieved = service.get_user_preferences(test_user_id)
            print(f"✅ Retrieved preferences: {retrieved}")
            
            return True
        else:
            print("❌ Preference storage failed")
            return False
            
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Supabase User Preferences")
    print("=" * 50)
    
    # Setup table
    if setup_supabase_table():
        print("\n✅ Supabase table setup completed")
        
        # Test service
        if test_preferences_service():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Run the test script: python test_supabase_preferences.py")
            print("2. Start your server and test the new functionality")
        else:
            print("\n⚠️  Table created but service test failed")
    else:
        print("\n❌ Setup failed. Please check your Supabase configuration.")

if __name__ == "__main__":
    main()
