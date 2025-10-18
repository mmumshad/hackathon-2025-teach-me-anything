"""
Supabase Service for Knowledge Graph Management
Direct Supabase client integration for database operations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlencode

# MCP imports removed to resolve dependency conflict
from supabase import create_client, Client
from config import Config

logger = logging.getLogger(__name__)

class SupabaseMCPService:
    """Service class for Supabase direct client integration and knowledge graph management"""
    
    def __init__(self):
        """Initialize Supabase service"""
        self.supabase_url = Config.SUPABASE_URL
        self.supabase_key = Config.SUPABASE_KEY
        # MCP API key removed - using direct Supabase client only
        
        # Initialize regular Supabase client
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        else:
            self.supabase = None
            logger.warning("Supabase credentials not found. Supabase features will be disabled.")
        
        # MCP client removed to resolve dependency conflict
    
    def is_available(self) -> bool:
        """Check if Supabase service is available"""
        return self.supabase is not None
    
    # MCP session method removed to resolve dependency conflict
    
    # MCP tools method removed to resolve dependency conflict
    
    # MCP search_docs method removed to resolve dependency conflict
    
    # MCP list_projects method removed to resolve dependency conflict
    
    # Knowledge Graph Management Methods
    
    def create_knowledge_graph_tables(self) -> bool:
        """Create tables for the study materials knowledge graph"""
        if not self.is_available():
            logger.error("Supabase not available")
            return False
        
        try:
            # Create study materials table
            study_materials_sql = """
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
            
            # Create material relationships table
            relationships_sql = """
            CREATE TABLE IF NOT EXISTS material_relationships (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_material_id UUID REFERENCES study_materials(id) ON DELETE CASCADE,
                target_material_id UUID REFERENCES study_materials(id) ON DELETE CASCADE,
                relationship_type TEXT NOT NULL CHECK (relationship_type IN ('prerequisite', 'similar', 'advanced', 'complementary')),
                similarity_score FLOAT CHECK (similarity_score >= 0 AND similarity_score <= 1),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(source_material_id, target_material_id, relationship_type)
            );
            """
            
            # Create learning concepts table
            concepts_sql = """
            CREATE TABLE IF NOT EXISTS learning_concepts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                concept_name TEXT UNIQUE NOT NULL,
                description TEXT,
                subject_area TEXT NOT NULL,
                grade_level TEXT,
                prerequisites TEXT[],
                related_concepts TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Create user learning history table
            user_history_sql = """
            CREATE TABLE IF NOT EXISTS user_learning_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                question TEXT NOT NULL,
                response TEXT,
                response_type TEXT CHECK (response_type IN ('text', 'video', 'audio', 'quiz')),
                subject TEXT,
                concepts_covered TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Execute SQL commands
            self.supabase.rpc('exec_sql', {'sql': study_materials_sql}).execute()
            self.supabase.rpc('exec_sql', {'sql': relationships_sql}).execute()
            self.supabase.rpc('exec_sql', {'sql': concepts_sql}).execute()
            self.supabase.rpc('exec_sql', {'sql': user_history_sql}).execute()
            
            logger.info("Knowledge graph tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating knowledge graph tables: {str(e)}")
            return False
    
    def add_study_material(
        self, 
        title: str, 
        material_type: str, 
        subject: str, 
        recommended_by: str,
        description: str = None,
        url: str = None,
        author: str = None,
        grade_level: str = None,
        rating: int = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Add a new study material to the knowledge graph"""
        if not self.is_available():
            return {"success": False, "error": "Supabase not available"}
        
        try:
            material_data = {
                "title": title,
                "type": material_type,
                "subject": subject,
                "recommended_by": recommended_by,
                "description": description,
                "url": url,
                "author": author,
                "grade_level": grade_level,
                "rating": rating,
                "tags": tags or []
            }
            
            result = self.supabase.table("study_materials").insert(material_data).execute()
            
            if result.data:
                logger.info(f"Added study material: {title}")
                return {
                    "success": True,
                    "material": result.data[0],
                    "message": f"Successfully added {material_type}: {title}"
                }
            else:
                return {"success": False, "error": "Failed to insert material"}
                
        except Exception as e:
            logger.error(f"Error adding study material: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_study_recommendations(
        self, 
        subject: str, 
        grade_level: str = None, 
        material_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get study material recommendations based on subject and grade level"""
        if not self.is_available():
            return []
        
        try:
            query = self.supabase.table("study_materials").select("*").eq("subject", subject)
            
            # Exclude records that are actually user requests (not real recommendations)
            bad_descriptions = [
                "could you please recommend me book on",
                "can you recommend me",
                "please recommend me",
                "suggest me",
                "help me find"
            ]
            
            for bad_desc in bad_descriptions:
                query = query.not_.ilike("description", f"%{bad_desc}%")
            
            if grade_level:
                query = query.eq("grade_level", grade_level)
            
            if material_type:
                query = query.eq("type", material_type)
            
            query = query.order("rating", desc=True).order("created_at", desc=True).limit(limit)
            
            result = query.execute()
            
            logger.info(f"Found {len(result.data)} study materials for {subject}")
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting study recommendations: {str(e)}")
            return []
    
    def add_user_learning_history(
        self, 
        user_id: str, 
        question: str, 
        response: str,
        response_type: str = "text",
        subject: str = None,
        concepts_covered: List[str] = None
    ) -> Dict[str, Any]:
        """Add user learning interaction to history"""
        if not self.is_available():
            return {"success": False, "error": "Supabase not available"}
        
        try:
            history_data = {
                "user_id": user_id,
                "question": question,
                "response": response,
                "response_type": response_type,
                "subject": subject,
                "concepts_covered": concepts_covered or []
            }
            
            result = self.supabase.table("user_learning_history").insert(history_data).execute()
            
            if result.data:
                logger.info(f"Added learning history for user {user_id}")
                return {"success": True, "history": result.data[0]}
            else:
                return {"success": False, "error": "Failed to insert history"}
                
        except Exception as e:
            logger.error(f"Error adding learning history: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_learning_patterns(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """Analyze user's learning patterns and suggest next topics"""
        if not self.is_available():
            return {"success": False, "error": "Supabase not available"}
        
        try:
            # Get user's learning history
            history_result = self.supabase.table("user_learning_history").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).limit(limit).execute()
            
            if not history_result.data:
                return {
                    "success": True,
                    "patterns": {
                        "subjects": [],
                        "concepts": [],
                        "suggestions": []
                    }
                }
            
            # Analyze patterns
            subjects = {}
            concepts = {}
            
            for record in history_result.data:
                subject = record.get("subject")
                if subject:
                    subjects[subject] = subjects.get(subject, 0) + 1
                
                concepts_covered = record.get("concepts_covered", [])
                for concept in concepts_covered:
                    concepts[concept] = concepts.get(concept, 0) + 1
            
            # Get top subjects and concepts
            top_subjects = sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:5]
            top_concepts = sorted(concepts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Generate suggestions based on patterns
            suggestions = []
            if top_subjects:
                primary_subject = top_subjects[0][0]
                # Get related materials for the primary subject
                related_materials = self.get_study_recommendations(primary_subject, limit=3)
                suggestions.extend([{
                    "type": "related_material",
                    "subject": primary_subject,
                    "materials": related_materials
                }])
            
            return {
                "success": True,
                "patterns": {
                    "subjects": top_subjects,
                    "concepts": top_concepts,
                    "suggestions": suggestions,
                    "total_interactions": len(history_result.data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def search_similar_materials(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar study materials using text search"""
        if not self.is_available():
            return []
        
        try:
            # Use PostgreSQL full-text search
            result = self.supabase.table("study_materials").select("*").text_search(
                "title,description", query
            ).limit(limit).execute()
            
            logger.info(f"Found {len(result.data)} similar materials for query: {query}")
            return result.data
            
        except Exception as e:
            logger.error(f"Error searching similar materials: {str(e)}")
            return []
    
    def detect_material_recommendation(self, message: str) -> Dict[str, Any]:
        """
        Detect if a user message contains a material recommendation
        
        Args:
            message: User's chat message
            
        Returns:
            Dictionary with recommendation details if detected, None otherwise
        """
        message_lower = message.lower()
        
        # Check if this is a request for recommendations (not a recommendation itself)
        request_keywords = [
            "could you recommend", "can you recommend", "please recommend", 
            "suggest", "what should i", "need recommendations", "looking for",
            "recommend me", "suggest me", "help me find", "i need", "i want",
            "could you please", "can you please", "please suggest"
        ]
        
        is_request = any(keyword in message_lower for keyword in request_keywords)
        if is_request:
            return None  # This is a request, not a recommendation
        
        # Keywords that indicate someone is GIVING a recommendation
        recommendation_keywords = [
            "i recommend", "i suggest", "great book", "amazing video", "check out",
            "you should read", "found this", "loved this", "this helped me", 
            "worth reading", "worth watching", "must read", "must watch", 
            "highly recommend", "definitely read", "try this", "this is good",
            "would like to recommend", "would like to suggest", "want to recommend",
            "want to suggest", "reccomend", "recomend"  # Handle common typos
        ]
        
        # Check if message contains recommendation keywords
        has_recommendation_keyword = any(keyword in message_lower for keyword in recommendation_keywords)
        
        if not has_recommendation_keyword:
            return None
        
        # Extract material type (check more specific types first)
        material_type = "book"  # default
        if any(word in message_lower for word in ["podcast", "listen", "episode"]):
            material_type = "podcast"
        elif any(word in message_lower for word in ["video", "youtube", "watch", "channel"]):
            material_type = "video"
        elif any(word in message_lower for word in ["article", "blog", "post", "website"]):
            material_type = "article"
        elif any(word in message_lower for word in ["course", "class", "tutorial"]):
            material_type = "course"
        
        # Extract subject
        subject = None
        if "physics" in message_lower:
            subject = "physics"
        elif "chemistry" in message_lower:
            subject = "chemistry"
        elif "biology" in message_lower:
            subject = "biology"
        elif "math" in message_lower or "mathematics" in message_lower:
            subject = "mathematics"
        elif "history" in message_lower:
            subject = "history"
        elif "english" in message_lower or "literature" in message_lower:
            subject = "english"
        elif "computer" in message_lower or "programming" in message_lower or "coding" in message_lower:
            subject = "computer_science"
        
        # Extract title (look for quoted text or capitalized words)
        import re
        
        # Look for quoted titles first
        quoted_titles = re.findall(r'"([^"]+)"', message)
        if quoted_titles:
            title = quoted_titles[0]
        else:
            # Look for titles after recommendation keywords
            title_patterns = [
                r"recommend\s+['\"]([^'\"]+)['\"]",  # recommend "Title"
                r"suggest\s+['\"]([^'\"]+)['\"]",    # suggest "Title"
                r"check out\s+['\"]([^'\"]+)['\"]",  # check out "Title"
                r"read\s+['\"]([^'\"]+)['\"]",       # read "Title"
                r"watch\s+['\"]([^'\"]+)['\"]",      # watch "Title"
                r"listen to\s+['\"]([^'\"]+)['\"]",  # listen to "Title"
            ]
            
            title = None
            for pattern in title_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    title = match.group(1)
                    break
            
            if not title:
                # Look for capitalized phrases that could be titles
                # Find phrases that start with capital letters and are followed by lowercase
                title_candidates = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
                
                # Filter out common words and short phrases
                common_words = {'I', 'You', 'This', 'That', 'The', 'A', 'An', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By'}
                title_candidates = [candidate for candidate in title_candidates if candidate not in common_words and len(candidate) > 3]
                
                if title_candidates:
                    # Take the longest meaningful phrase
                    title = max(title_candidates, key=len)
                else:
                    # Fallback: look for meaningful phrases after recommendation words
                    words = message.split()
                    title_words = []
                    in_title = False
                    
                    for word in words:
                        # Start collecting after recommendation keywords
                        if any(keyword in word.lower() for keyword in ['recommend', 'suggest', 'check', 'read', 'watch', 'listen']):
                            in_title = True
                            continue
                        
                        if in_title:
                            # Stop at punctuation or common words
                            if word in ['.', ',', '!', '?', '-', 'by', 'for', 'about', 'on', 'in', 'at']:
                                break
                            if word[0].isupper() and len(word) > 2:
                                title_words.append(word)
                            elif title_words:  # Stop at first non-capitalized word after finding some
                                break
                    
                    title = " ".join(title_words) if title_words else "Recommended Material"
        
        # Extract URL if present
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, message)
        url = urls[0] if urls else None
        
        # Extract author (look for "by [author]" pattern)
        author_match = re.search(r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', message)
        author = author_match.group(1) if author_match else None
        
        # Extract rating if mentioned
        rating_match = re.search(r'(\d+)/5|(\d+)\s*stars?|rating[:\s]*(\d+)', message_lower)
        rating = None
        if rating_match:
            rating = int(rating_match.group(1) or rating_match.group(2) or rating_match.group(3))
            rating = min(max(rating, 1), 5)  # Clamp between 1-5
        
        # Extract grade level if mentioned
        grade_level = None
        if any(grade in message_lower for grade in ["elementary", "primary", "1st grade", "2nd grade", "3rd grade", "4th grade", "5th grade"]):
            grade_level = "elementary"
        elif any(grade in message_lower for grade in ["middle school", "6th grade", "7th grade", "8th grade"]):
            grade_level = "middle school"
        elif any(grade in message_lower for grade in ["high school", "9th grade", "10th grade", "11th grade", "12th grade"]):
            grade_level = "high school"
        elif any(grade in message_lower for grade in ["college", "university", "undergraduate"]):
            grade_level = "college"
        
        # Extract tags/keywords
        tags = []
        if "beginner" in message_lower or "basic" in message_lower:
            tags.append("beginner")
        if "advanced" in message_lower or "expert" in message_lower:
            tags.append("advanced")
        if "fun" in message_lower or "interesting" in message_lower:
            tags.append("engaging")
        if "free" in message_lower:
            tags.append("free")
        
        return {
            "title": title,
            "type": material_type,
            "subject": subject,
            "url": url,
            "author": author,
            "rating": rating,
            "grade_level": grade_level,
            "tags": tags,
            "description": message[:200] + "..." if len(message) > 200 else message,
            "confidence": 0.8 if has_recommendation_keyword and title else 0.5
        }
    
    def process_chat_for_recommendations(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a chat message to detect and add material recommendations
        
        Args:
            user_id: User ID
            message: Chat message content
            
        Returns:
            Dictionary with processing results
        """
        if not self.is_available():
            return {"success": False, "error": "Supabase not available"}
        
        # Detect recommendation in the message
        recommendation = self.detect_material_recommendation(message)
        
        if not recommendation:
            return {"success": True, "recommendation_detected": False}
        
        # Add the recommendation to the knowledge graph
        try:
            result = self.add_study_material(
                title=recommendation["title"],
                material_type=recommendation["type"],
                subject=recommendation["subject"] or "general",
                recommended_by=user_id,
                description=recommendation["description"],
                url=recommendation["url"],
                author=recommendation["author"],
                grade_level=recommendation["grade_level"],
                rating=recommendation["rating"],
                tags=recommendation["tags"]
            )
            
            if result["success"]:
                logger.info(f"Auto-detected and added recommendation: {recommendation['title']}")
                return {
                    "success": True,
                    "recommendation_detected": True,
                    "material": result["material"],
                    "confidence": recommendation["confidence"]
                }
            else:
                return {
                    "success": False,
                    "recommendation_detected": True,
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"Error processing recommendation: {str(e)}")
            return {
                "success": False,
                "recommendation_detected": True,
                "error": str(e)
            }
    
    # MCP close session method removed to resolve dependency conflict
