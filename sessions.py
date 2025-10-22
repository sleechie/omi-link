"""
Session management for Omi-Jarvis conversations

Maps Omi device session IDs to OpenAI Conversation IDs for persistent conversation history.
Uses OpenAI Conversations API for automatic context management.
"""

import os
import psycopg2
from agents.memory import OpenAIConversationsSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(DATABASE_URL)


def get_session_mapping(omi_session_id: str):
    """
    Get OpenAI conversation_id for an Omi session
    
    Args:
        omi_session_id: Session ID from Omi device
        
    Returns:
        str: OpenAI conversation_id if exists, None otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT openai_conversation_id FROM sessions WHERE omi_session_id = %s"
        cursor.execute(query, (omi_session_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result else None
        
    except Exception as e:
        print(f"ERROR getting session mapping: {str(e)}")
        return None


def save_session_mapping(omi_session_id: str, openai_conversation_id: str):
    """
    Save or update Omi session -> OpenAI conversation mapping
    
    Args:
        omi_session_id: Session ID from Omi device
        openai_conversation_id: OpenAI conversation ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO sessions (omi_session_id, openai_conversation_id, last_used_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (omi_session_id) 
            DO UPDATE SET openai_conversation_id = EXCLUDED.openai_conversation_id,
                          last_used_at = CURRENT_TIMESTAMP
        """
        
        cursor.execute(query, (omi_session_id, openai_conversation_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"Saved session mapping: {omi_session_id} -> {openai_conversation_id}")
        return True
        
    except Exception as e:
        print(f"ERROR saving session mapping: {str(e)}")
        return False


def get_or_create_session(omi_session_id: str) -> OpenAIConversationsSession:
    """
    Get existing OpenAI Conversation session for Omi device or create a new one.
    OpenAI handles all conversation persistence automatically.
    
    Args:
        omi_session_id: Session ID from Omi device
        
    Returns:
        OpenAIConversationsSession: Session object (new or resumed)
    """
    # Handle missing or empty session IDs
    if not omi_session_id or omi_session_id.strip() == "":
        import uuid
        omi_session_id = f"unknown_{uuid.uuid4().hex[:8]}"
        print(f"Warning: Empty session ID, using generated ID: {omi_session_id}")
    
    # Check database for existing conversation
    existing_conv_id = get_session_mapping(omi_session_id)
    
    if existing_conv_id:
        print(f"Resuming conversation {existing_conv_id} for Omi session {omi_session_id}")
        return OpenAIConversationsSession(conversation_id=existing_conv_id)
    else:
        print(f"Creating new conversation for Omi session {omi_session_id}")
        # Create NEW conversation - OpenAI will generate the conversation_id
        return OpenAIConversationsSession()


def save_conversation_id_for_session(omi_session_id: str, session: OpenAIConversationsSession) -> bool:
    """
    Extract and save OpenAI conversation ID from session object after first use
    
    Args:
        omi_session_id: Session ID from Omi device
        session: OpenAI Conversations session object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract the OpenAI-generated conversation_id from session
        openai_conv_id = None
        
        # Access the _session_id attribute (contains the OpenAI conversation ID)
        if hasattr(session, '_session_id'):
            openai_conv_id = getattr(session, '_session_id')
        
        if openai_conv_id:
            return save_session_mapping(omi_session_id, openai_conv_id)
        else:
            print(f"Warning: Could not extract conversation ID from session for {omi_session_id}")
            return False
            
    except Exception as e:
        print(f"ERROR saving conversation ID for session {omi_session_id}: {str(e)}")
        return False


def get_session_count() -> int:
    """
    Get total number of tracked conversations
    
    Returns:
        int: Number of Omi sessions tracked
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"ERROR getting session count: {str(e)}")
        return 0


if __name__ == "__main__":
    # Simple test
    print("=== Session Manager Test ===")
    print("Testing OpenAI Conversations API integration with PostgreSQL...")
    
    # Test conversation creation
    test_session_id = "test_omi_session_123"
    session1 = get_or_create_session(test_session_id)
    print(f"Created/retrieved OpenAI conversation for Omi session {test_session_id}")
    
    # Test conversation retrieval
    session2 = get_or_create_session(test_session_id)
    print(f"Retrieved OpenAI conversation for Omi session {test_session_id}")
    
    # Show session count
    print(f"\nTotal conversations tracked: {get_session_count()}")
    print("OpenAI handles all conversation persistence automatically!")

