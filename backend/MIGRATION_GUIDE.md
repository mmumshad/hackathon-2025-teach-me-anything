# Migration Guide: Mem0 to Supabase User Preferences

## Overview
This guide covers the migration from Mem0 to Supabase for user preferences storage and the implementation of intelligent preference extraction using OpenAI LLM.

## Changes Made

### 1. New Services Created

#### `SupabaseUserPreferencesService`
- **File**: `services/supabase_user_preferences_service.py`
- **Purpose**: Handles user preference storage and retrieval using Supabase
- **Features**:
  - Store/retrieve user preferences
  - Update specific preferences
  - Video/audio generation logic
  - Response personalization

#### `IntelligentPreferenceExtractionService`
- **File**: `services/intelligent_preference_extraction_service.py`
- **Purpose**: Uses OpenAI LLM to intelligently extract preferences from user messages
- **Features**:
  - Extract name, grade level, language, learning style, subjects
  - Merge preferences intelligently
  - Conservative extraction (only clear information)

### 2. Database Schema

#### Supabase Table: `user_preferences`
```sql
CREATE TABLE user_preferences (
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
```

### 3. Updated Endpoints

All user preference endpoints now use Supabase:
- `POST /api/v1/user/preferences` - Store preferences
- `GET /api/v1/user/preferences` - Retrieve preferences
- `GET /api/v1/user/context` - Get user context

### 4. Intelligent Preference Extraction

The system now automatically extracts preferences from user messages using OpenAI:

**Example Messages and Extracted Preferences:**

| Message | Extracted Preferences |
|---------|----------------------|
| "Hi, my name is Alice and I'm in high school. I prefer video learning for physics." | `{"name": "Alice", "grade_level": "high", "learning_style": "video", "preferred_subjects": ["physics"]}` |
| "I'm John, a college student. I like reading books about mathematics." | `{"name": "John", "grade_level": "college", "learning_style": "reading", "preferred_subjects": ["mathematics"]}` |
| "Call me Sarah. I'm in middle school and I love audio content for learning history." | `{"name": "Sarah", "grade_level": "middle", "learning_style": "audio", "preferred_subjects": ["history"]}` |

## Setup Instructions

### 1. Create Supabase Table
Run the SQL script in your Supabase dashboard:
```bash
# Execute the contents of supabase_user_preferences_table.sql
```

### 2. Environment Variables
Ensure these are set in your `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Install Dependencies
The existing dependencies should be sufficient. No new packages required.

### 4. Test the Migration
Run the test script:
```bash
cd backend
python test_supabase_preferences.py
```

## Key Improvements

### 1. **Intelligent Extraction**
- **Before**: Keyword matching with limited patterns
- **After**: OpenAI LLM understands context and extracts meaningful preferences

### 2. **Reliable Storage**
- **Before**: Mem0 API issues with filters and retrieval
- **After**: Direct Supabase database with reliable queries

### 3. **Better Performance**
- **Before**: Multiple API calls to Mem0 with potential failures
- **After**: Single database queries with fallback to defaults

### 4. **Enhanced Personalization**
- **Before**: Basic name insertion
- **After**: Context-aware preference extraction and intelligent merging

## Migration Benefits

1. **Eliminates Mem0 API Issues**: No more 400 Bad Request errors
2. **Intelligent Preference Detection**: Automatically learns from user messages
3. **Better User Experience**: Seamless preference collection without explicit forms
4. **Reliable Data Storage**: Direct database access with proper indexing
5. **Scalable Architecture**: Can handle more complex preference structures

## Testing

The test script (`test_supabase_preferences.py`) covers:
- ✅ Preference storage and retrieval
- ✅ Intelligent extraction from various message types
- ✅ User context generation
- ✅ Video/audio generation logic
- ✅ Preference merging

## Rollback Plan

If needed, you can rollback by:
1. Reverting the service imports in `main.py`
2. Changing service calls back to `mem0_service`
3. The Mem0 service remains intact for fallback

## Next Steps

1. **Monitor Performance**: Track preference extraction accuracy
2. **Enhance Extraction**: Add more sophisticated preference patterns
3. **User Feedback**: Implement preference correction mechanisms
4. **Analytics**: Track user preference patterns for insights

## Support

For issues or questions:
1. Check the test script output for specific errors
2. Verify Supabase table creation and permissions
3. Ensure OpenAI API key is valid and has sufficient credits
4. Review server logs for detailed error messages
