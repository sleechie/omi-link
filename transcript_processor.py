import time
import threading
from datetime import datetime
import db
import ai_handler

# Configuration
POLL_INTERVAL = 10  # seconds
RUNNING = False

# Activation phrases (case-insensitive)
ACTIVATION_PHRASES = [
    "hey jarvis",
    "hey, jarvis",
    "hi jarvis",
    "hi, jarvis",
    "hello jarvis",
    "hello, jarvis",
    "okay jarvis",
    "okay, jarvis",
    "ok jarvis",
    "ok, jarvis",
]

def process_transcripts():
    """
    Main processing function that runs every POLL_INTERVAL seconds
    Checks for unprocessed transcripts, batches them, and sends to AI
    """
    try:
        # Get unprocessed transcripts
        transcripts = db.get_unprocessed_transcripts()
        
        if not transcripts:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new transcripts to process")
            return
        
        print("\n" + "="*60)
        print(f"PROCESSING {len(transcripts)} NEW TRANSCRIPT(S)")
        print("="*60)
        
        # IMPORTANT: Mark as processed FIRST to prevent duplicate processing
        # This prevents race conditions where new transcripts arrive during AI processing
        transcript_ids = [t['id'] for t in transcripts]
        db.mark_transcripts_processed(transcript_ids, None)
        
        # Format transcripts into user message
        user_message = ai_handler.format_transcripts_for_ai(transcripts)
        
        if not user_message.strip():
            print("Warning: Transcripts formatted to empty message, skipping")
            return
        
        # Check if message contains any activation phrase
        user_message_lower = user_message.lower()
        activated = False
        detected_phrase = None
        
        for phrase in ACTIVATION_PHRASES:
            if phrase in user_message_lower:
                activated = True
                detected_phrase = phrase
                break
        
        if not activated:
            print(f"Skipping AI call - no activation phrase detected")
            print(f"Transcript: {user_message[:100]}...")
            # Already marked as processed at the start
            return
        
        print(f"Activation phrase '{detected_phrase}' detected!")
        
        # Get session ID from transcripts
        session_id = transcripts[0].get('session_id', 'unknown') if transcripts else 'unknown'
        
        # Send to Jarvis - SDK handles tools automatically!
        ai_response = ai_handler.send_to_jarvis(user_message, session_id)
        
        if ai_response is None:
            print("ERROR: Failed to get AI response, will retry next cycle")
            return
        
        # Save user message
        user_message_id = db.save_message('user', user_message)
        
        if user_message_id is None:
            print("ERROR: Failed to save user message")
            return
        
        # ALWAYS text the AI response to user
        print("\n" + "="*60)
        print("SENDING AI RESPONSE VIA SMS")
        print("="*60)
        print(f"Response: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")
        print("="*60 + "\n")
        
        import sms
        sms_result = sms.send_sms(ai_response)
        
        if sms_result and sms_result.get('success'):
            print(f"✅ AI response texted successfully! Text ID: {sms_result.get('textId')}")
        else:
            error = sms_result.get('error', 'Unknown error') if sms_result else 'Failed'
            print(f"❌ Failed to text AI response: {error}")
        
        # Save AI response (tool execution handled by SDK)
        ai_message_id = db.save_message('ai', ai_response)
        
        if ai_message_id is None:
            print("ERROR: Failed to save AI message")
        
        # Update transcripts to link them to the user message
        # (already marked as processed at the start)
        db.mark_transcripts_processed(transcript_ids, user_message_id)
        
        print(f"Successfully processed {len(transcripts)} transcript(s)")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"ERROR in process_transcripts: {str(e)}")
        import traceback
        traceback.print_exc()

def polling_loop():
    """
    Background polling loop that runs continuously
    """
    global RUNNING
    
    print("\n" + "="*60)
    print("TRANSCRIPT PROCESSOR STARTED")
    print(f"Polling every {POLL_INTERVAL} seconds for new transcripts")
    print("="*60 + "\n")
    
    while RUNNING:
        try:
            process_transcripts()
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\nTranscript processor interrupted")
            break
        except Exception as e:
            print(f"ERROR in polling loop: {str(e)}")
            time.sleep(POLL_INTERVAL)
    
    print("\nTranscript processor stopped")

def start_processor():
    """
    Start the background transcript processor thread
    """
    global RUNNING
    
    if RUNNING:
        print("Transcript processor already running")
        return
    
    RUNNING = True
    
    # Start polling thread
    thread = threading.Thread(target=polling_loop, daemon=True)
    thread.start()
    
    return thread

def stop_processor():
    """
    Stop the background transcript processor
    """
    global RUNNING
    RUNNING = False
    print("Stopping transcript processor...")

def set_poll_interval(seconds):
    """
    Set the polling interval (useful for testing)
    
    Args:
        seconds (int): Poll interval in seconds
    """
    global POLL_INTERVAL
    POLL_INTERVAL = seconds
    print(f"Poll interval set to {seconds} seconds")

