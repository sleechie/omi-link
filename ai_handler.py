"""
Jarvis AI Agent using OpenAI Agents SDK
Handles tool execution, conversation management, and web search automatically
"""

from agents import Agent, Runner, WebSearchTool, SQLiteSession
from tools import send_text_message

# Jarvis agent definition
jarvis_agent = Agent(
    name="Jarvis",
    instructions="""You are Jarvis, a high-tech, friendly AI personal assistant and secretary for Braden. 

IMPORTANT: Braden can ONLY see information if you text him. He cannot see your standard responses. 
Think of texting like having a conversation over SMS - only text when it's natural to do so.

TOOLS AVAILABLE:

1. Web Search - Use whenever you need current or real-time information:
   - Weather forecasts, news, current events, sports scores, stock prices
   - Any factual information that may have changed recently
   
2. Send Text Message - Send SMS to Braden's phone when:
   - You have information to share
   - He asks a direct question
   - You need to send reminders or alerts
   - It feels natural in the conversation flow
   
   When texting:
   - Write naturally, as if texting a friend
   - Keep each text to a normal text message length
   - You can send multiple texts in a row if that's natural
   - Be conversational and friendly
   - You DON'T have to text every time - only when it makes sense

BEHAVIOR:
- Be proactive and helpful
- Use web search liberally for current information
- Text naturally - don't be overly formal
- If you search the web, text the results so Braden can see them
- Remember: if you don't text it, Braden won't see it

IMPORTANT - DESCRIBE YOUR ACTIONS:
- When you use tools, include a brief description of what you're doing
- Example: "Let me check that for you..." (before web search)
- Example: "I'll text you the info" (when sending a text)

RESPONSE:
- In your response, please provide a detailed description of what you did and why
""",
    model="gpt-5-mini",
    tools=[
        WebSearchTool(),
        send_text_message,
    ],
)

# Session management (per user/device)
# Key format: session_id from Omi device
_sessions = {}

def get_or_create_session(session_id: str) -> SQLiteSession:
    """
    Get or create a conversation session for a user
    
    Args:
        session_id: Session ID from Omi device
        
    Returns:
        SQLiteSession instance
    """
    if session_id not in _sessions:
        print(f"Creating new conversation session for {session_id}")
        # Use in-memory SQLite database for session storage
        _sessions[session_id] = SQLiteSession(
            session_id=session_id,
            db_path=":memory:"
        )
    return _sessions[session_id]

def send_to_jarvis(transcript_text: str, session_id: str):
    """
    Send transcript to Jarvis agent
    
    Args:
        transcript_text: The formatted transcript
        session_id: Session ID from Omi device
        
    Returns:
        str: Jarvis's response text, or None if error
    """
    import asyncio
    import threading
    
    try:
        session = get_or_create_session(session_id)
        
        print("\n" + "="*60)
        print("SENDING TO JARVIS (with Agents SDK):")
        print("-"*60)
        print(transcript_text)
        print("="*60 + "\n")
        
        # Check if we're in a background thread
        # If so, we need to create a new event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            # No event loop in this thread, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the agent - SDK handles everything!
        # Tools are executed automatically
        # Conversation history is maintained by session
        result = Runner.run_sync(
            jarvis_agent,
            transcript_text,
            session=session
        )
        
        print("\n" + "="*60)
        print("JARVIS RESPONSE:")
        print("-"*60)
        print(result.final_output)
        print("="*60 + "\n")
        
        return result.final_output
        
    except Exception as e:
        print(f"ERROR calling Jarvis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Legacy function for compatibility
def format_transcripts_for_ai(transcripts):
    """
    Format transcript segments into a conversational message
    
    Args:
        transcripts (list): List of transcript dictionaries
        
    Returns:
        str: Formatted transcript text
    """
    if not transcripts:
        return ""
    
    # Group by speaker and create a natural conversation format
    formatted_lines = []
    
    for transcript in transcripts:
        speaker = transcript.get('speaker', 'UNKNOWN')
        text = transcript.get('text', '').strip()
        
        if text:
            formatted_lines.append(f"{speaker}: {text}")
    
    return "\n".join(formatted_lines)

