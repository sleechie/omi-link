"""
Tools for Jarvis agent
Uses @function_tool decorator from OpenAI Agents SDK
"""

from agents import function_tool
import sms

@function_tool
def send_text_message(message: str) -> str:
    """
    Send an SMS text message to Braden's phone.
    Use this when you have information to share with him.
    
    Args:
        message: The text message to send. Write naturally as if texting a friend.
    
    Returns:
        Status message indicating success or failure
    """
    print("\n" + "="*60)
    print("📱 SEND TEXT MESSAGE TOOL EXECUTED")
    print("="*60)
    print(f"Message Content:")
    print("-"*60)
    print(message)
    print("-"*60)
    print(f"Message Length: {len(message)} characters")
    print("="*60 + "\n")
    
    result = sms.send_sms(message)
    
    if result and result.get('success'):
        print(f"✅ Text sent successfully! Text ID: {result.get('textId')}")
        print(f"   Quota Remaining: {result.get('quotaRemaining')}\n")
        return "Text message sent successfully"
    else:
        error = result.get('error', 'Unknown error') if result else 'Failed'
        print(f"❌ Text failed: {error}\n")
        return f"Failed to send text: {error}"

