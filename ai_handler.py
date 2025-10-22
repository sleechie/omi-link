"""
Jarvis AI Agent using OpenAI Agents SDK
Handles tool execution, conversation management, and web search automatically
"""

from agents import Agent, Runner, WebSearchTool
from tools import send_text_message
import sessions

# Jarvis agent definition
jarvis_agent = Agent(
    name="Jarvis",
    instructions="""
    
You are Jarvis, a high-tech, friendly AI personal assistant and secretary for Braden. 

IMPORTANT: Your responses are automatically sent to Braden via text message. 
Keep your responses concise and text-message friendly.

TOOLS AVAILABLE:

1. Web Search - Use whenever you need current or real-time information:
   - Weather forecasts, news, current events, sports scores, stock prices
   - Any factual information that may have changed recently
   
2. Send Text Message - Use this tool to send ADDITIONAL texts during processing:
   - Send immediate updates while you're still working on something
   - Send multiple pieces of information separately
   - For example: text a quick "Looking that up..." while doing a web search
   
   Your final response is ALWAYS texted automatically, so you don't need to use this tool 
   for your main response - only for extra messages during processing.

BEHAVIOR:
- Be proactive and helpful
- Use web search liberally for current information
- Keep responses conversational and concise (like texting a friend)
- Your response goes directly to Braden's phone, so write naturally

RESPONSE FORMAT:
- Keep it brief and text-message friendly
- Answer the question directly
- If you used web search, mention what you found
- No need to describe what you're doing unless it's helpful context
""",
    model="gpt-5-mini",
    tools=[
        WebSearchTool(),
        send_text_message,
    ],
)

# Note: Session management is now handled by sessions.py module
# Uses OpenAI Conversations API with PostgreSQL persistence

def send_to_jarvis(transcript_text: str, omi_session_id: str):
    """
    Send transcript to Jarvis agent with persistent conversation history
    
    Args:
        transcript_text: The formatted transcript
        omi_session_id: Session ID from Omi device
        
    Returns:
        str: Jarvis's response text, or None if error
    """
    import asyncio
    
    try:
        # Get or create OpenAI Conversation session (with database persistence)
        session = sessions.get_or_create_session(omi_session_id)
        
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
        # Conversation history is maintained by OpenAI Conversations API
        result = Runner.run_sync(
            jarvis_agent,
            transcript_text,
            session=session
        )
        
        # Save OpenAI conversation ID to database after first use
        sessions.save_conversation_id_for_session(omi_session_id, session)
        
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

