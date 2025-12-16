import os
import sys
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_call():
    # Credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    # Check for token
    if not auth_token:
        print("❌ Error: TWILIO_AUTH_TOKEN not found in environment.")
        print("Please provide it when running the script or add it to .env")
        print("Usage: TWILIO_AUTH_TOKEN=your_token python test_twilio_direct.py")
        return

    try:
        print(f"🔹 Authenticating with SID: {account_sid}...")
        client = Client(account_sid, auth_token)

        # Phone numbers
        from_number = '+19528661775' # Your new purchased number
        to_number = '+16173653176'   # The US number you want to test (Mauricio Cuevas?)
        
        print(f"📞 Initiating call from {from_number} to {to_number}...")
        
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url='http://demo.twilio.com/docs/voice.xml' # TwiML to play a simple message
        )

        print(f"✅ Call initiated successfully!")
        print(f"🔹 Call SID: {call.sid}")
        print(f"🔹 Status: {call.status}")
        
    except Exception as e:
        print(f"❌ Error initiating call: {e}")
        # Try to get the Twilio Request ID if it exists in the error object
        if hasattr(e, 'msg') and e.msg:
            print(f"🔹 Error Message: {e.msg}")
        if hasattr(e, 'code'):
            print(f"🔹 Error Code: {e.code}")
        if hasattr(e, 'details'):
            print(f"🔹 More Info: {e.details}")
            
        # Requests library exception usually has a response object
        if hasattr(e, 'response') and e.response is not None:
             print(f"🔹 Twilio-Request-Id: {e.response.headers.get('Twilio-Request-Id', 'Not found')}")
             print(f"🔹 HTTP Status: {e.response.status_code}")

if __name__ == "__main__":
    test_call()
