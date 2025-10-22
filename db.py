import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Get a database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(database_url)

def init_db():
    """Initialize database tables from schema.sql"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        cursor.execute(schema)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"ERROR initializing database: {str(e)}")
        return False

def save_transcript_segment(segment_data):
    """
    Save a transcript segment to the database
    
    Args:
        segment_data (dict): Segment data from Omi webhook
        
    Returns:
        int: ID of saved transcript, or None if error
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO transcripts 
            (segment_id, text, speaker, speaker_id, is_user, start_time, end_time, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (segment_id) DO NOTHING
            RETURNING id
        """
        
        cursor.execute(query, (
            segment_data.get('id'),
            segment_data.get('text', ''),
            segment_data.get('speaker', 'UNKNOWN'),
            segment_data.get('speaker_id', 0),
            segment_data.get('is_user', False),
            segment_data.get('start', 0.0),
            segment_data.get('end', 0.0),
            segment_data.get('session_id')
        ))
        
        result = cursor.fetchone()
        conn.commit()
        
        transcript_id = result[0] if result else None
        
        cursor.close()
        conn.close()
        
        if transcript_id:
            print(f"Saved transcript segment {segment_data.get('id')} to database")
        else:
            print(f"Transcript segment {segment_data.get('id')} already exists")
        
        return transcript_id
        
    except Exception as e:
        print(f"ERROR saving transcript segment: {str(e)}")
        return None

def get_unprocessed_transcripts():
    """
    Get all unprocessed transcripts
    
    Returns:
        list: List of unprocessed transcript dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT * FROM transcripts 
            WHERE processed = FALSE 
            ORDER BY received_at ASC
        """
        
        cursor.execute(query)
        transcripts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(t) for t in transcripts]
        
    except Exception as e:
        print(f"ERROR getting unprocessed transcripts: {str(e)}")
        return []

def mark_transcripts_processed(transcript_ids, message_id):
    """
    Mark transcripts as processed and link them to a message
    
    Args:
        transcript_ids (list): List of transcript IDs to mark as processed
        message_id (int): ID of the message these transcripts belong to
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE transcripts 
            SET processed = TRUE, message_id = %s 
            WHERE id = ANY(%s)
        """
        
        cursor.execute(query, (message_id, transcript_ids))
        conn.commit()
        
        rows_updated = cursor.rowcount
        
        cursor.close()
        conn.close()
        
        print(f"Marked {rows_updated} transcripts as processed")
        return True
        
    except Exception as e:
        print(f"ERROR marking transcripts as processed: {str(e)}")
        return False

def save_message(message_type, message_text, tool_executions=None):
    """
    Save a message (user or AI) to the database
    
    Args:
        message_type (str): 'user' or 'ai'
        message_text (str): The message content
        tool_executions (list, optional): List of tool names that were executed (not used with Agents SDK)
        
    Returns:
        int: ID of saved message, or None if error
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Note: tool_executions is kept for backwards compatibility but not used with Agents SDK
        # The SDK handles tool execution internally
        tool_executions_str = None
        if tool_executions and len(tool_executions) > 0:
            tool_executions_str = ','.join(tool_executions)
        
        query = """
            INSERT INTO messages (message_type, message_text, tool_executions)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        
        cursor.execute(query, (message_type, message_text, tool_executions_str))
        message_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Saved {message_type} message (ID: {message_id})")
        return message_id
        
    except Exception as e:
        print(f"ERROR saving message: {str(e)}")
        return None

def get_conversation_history(limit=10):
    """
    Get recent conversation history
    
    Args:
        limit (int): Maximum number of messages to retrieve
        
    Returns:
        list: List of message dictionaries, ordered by timestamp (oldest first)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT message_type, message_text, timestamp
            FROM messages
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        messages = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Return in chronological order (oldest first)
        return [dict(m) for m in reversed(messages)]
        
    except Exception as e:
        print(f"ERROR getting conversation history: {str(e)}")
        return []

def get_all_messages():
    """
    Get all messages for debugging/viewing
    
    Returns:
        list: List of all message dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM messages ORDER BY timestamp ASC"
        cursor.execute(query)
        messages = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(m) for m in messages]
        
    except Exception as e:
        print(f"ERROR getting all messages: {str(e)}")
        return []

