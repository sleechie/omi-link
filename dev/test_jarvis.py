"""
Simple script to manually test Jarvis agent
Run from project root: python dev/test_jarvis.py
"""

import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
import ai_handler

# Load environment variables
load_dotenv()

def test_jarvis(message: str, session_id: str = "test_session"):
    """
    Send a message to Jarvis and print the response
    
    Args:
        message: The message to send to Jarvis
        session_id: Session ID (default: "test_session")
    """
    print("\n" + "="*60)
    print("TESTING JARVIS")
    print("="*60)
    print(f"Session ID: {session_id}")
    print(f"Your message: {message}")
    print("="*60 + "\n")
    
    # Send to Jarvis
    response = ai_handler.send_to_jarvis(message, session_id)
    
    if response:
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        print(f"Jarvis response: {response}")
        print("="*60 + "\n")
    else:
        print("\nERROR: Failed to get response from Jarvis\n")

def interactive_mode():
    """
    Interactive mode - chat with Jarvis continuously
    """
    session_id = "interactive_test"
    print("\n" + "="*60)
    print("JARVIS INTERACTIVE TEST MODE")
    print("="*60)
    print("Type your messages and press Enter.")
    print("Type 'exit' or 'quit' to stop.")
    print("Type 'new' to start a new session.")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye!\n")
                break
            
            if user_input.lower() == 'new':
                import time
                session_id = f"interactive_{int(time.time())}"
                print(f"\nStarted new session: {session_id}\n")
                continue
            
            if not user_input:
                continue
            
            response = ai_handler.send_to_jarvis(user_input, session_id)
            
            if response:
                print(f"\nJarvis: {response}\n")
            else:
                print("\nERROR: Failed to get response from Jarvis\n")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"\nERROR: {e}\n")

if __name__ == "__main__":
    # Check if message provided as command line argument
    if len(sys.argv) > 1:
        # Command line mode - send single message
        message = " ".join(sys.argv[1:])
        test_jarvis(message)
    else:
        # Interactive mode - continuous conversation
        interactive_mode()

