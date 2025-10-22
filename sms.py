"""
SMS module using Textbelt API
Sends text messages with AI responses
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_sms(message, phone_number=None):
    """
    Send an SMS using Textbelt API
    
    Args:
        message (str): The message to send
        phone_number (str, optional): Phone number to send to. 
                                      If None, uses PHONE_NUMBER from env
    
    Returns:
        dict: Response from Textbelt API, or None if error
    """
    try:
        # Get configuration from environment
        if phone_number is None:
            phone_number = os.getenv('PHONE_NUMBER')
        
        textbelt_key = os.getenv('TEXTBELT_API_KEY', 'textbelt')
        
        if not phone_number:
            print("ERROR: No phone number configured")
            return None
        
        # Prepare the request
        url = 'https://textbelt.com/text'
        data = {
            'phone': phone_number,
            'message': message,
            'key': textbelt_key,
        }
        
        print(f"Sending SMS to {phone_number}...")
        
        # Send the request
        response = requests.post(url, data=data)
        result = response.json()
        
        # Check if successful
        if result.get('success'):
            print(f"SMS sent successfully! Text ID: {result.get('textId')}")
            print(f"Quota remaining: {result.get('quotaRemaining')}")
            return result
        else:
            error = result.get('error', 'Unknown error')
            print(f"ERROR sending SMS: {error}")
            if 'quotaRemaining' in result:
                print(f"Quota remaining: {result['quotaRemaining']}")
            return None
            
    except Exception as e:
        print(f"ERROR sending SMS: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_sms():
    """
    Test SMS sending with a simple message
    
    Returns:
        bool: True if test successful, False otherwise
    """
    test_message = "This is a test message from your Omi AI system!"
    result = send_sms(test_message)
    return result is not None

if __name__ == "__main__":
    # Test the SMS functionality
    print("Testing SMS functionality...")
    if test_sms():
        print("SMS test successful!")
    else:
        print("SMS test failed!")

