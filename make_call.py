"""
Simple script to make a single outbound call using ElevenLabs API.
Usage: python make_call.py [customer_id_or_phone]
"""

import sys
import os
import requests
from database import get_supabase_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
AGENT_PHONE_NUMBER_ID = os.getenv("AGENT_PHONE_NUMBER_ID")  # Twilio phone number ID in ElevenLabs

def make_call(phone_number: str, customer_name: str):
    """
    Make a single outbound call using ElevenLabs Conversational AI.
    
    Args:
        phone_number: Phone number in E.164 format (e.g., +15551234567)
        customer_name: Customer's name for personalization
    """
    print("=" * 60)
    print("📞 ElevenLabs Outbound Call")
    print("=" * 60)
    print(f"Customer: {customer_name}")
    print(f"Phone: {phone_number}")
    print(f"Agent ID: {ELEVENLABS_AGENT_ID}")
    print()
    
    if not AGENT_PHONE_NUMBER_ID:
        print("⚠️  Warning: AGENT_PHONE_NUMBER_ID not set in .env")
        print("   The call might fail without this ID")
        print()
    
    # ElevenLabs API endpoint for Twilio outbound calls
    url = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "agent_id": ELEVENLABS_AGENT_ID,
        "to_number": phone_number,
    }
    
    # Add agent_phone_number_id if configured
    if AGENT_PHONE_NUMBER_ID:
        payload["agent_phone_number_id"] = AGENT_PHONE_NUMBER_ID
    
    # Add custom variables for the conversation
    # These can be referenced in the ElevenLabs prompt and tools
    payload["conversation_config_override"] = {
        "agent": {
            "prompt": {
                "prompt": f"You are Jess, calling {customer_name}. Use their name in the greeting."
            },
            "first_message": f"Hi! <break time=\"0.3s\"/> I was hoping to catch {customer_name}? <break time=\"0.3s\"/> Is that you?",
            "dynamic_variables": {
                "phone_number": phone_number,
                "customer_name": customer_name
            }
        }
    }
    
    print("Initiating call...")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Call initiated successfully!")
            print()
            print("Response:")
            print(f"  Conversation ID: {data.get('conversation_id', 'N/A')}")
            if 'status' in data:
                print(f"  Status: {data['status']}")
            print()
            print("Full response:")
            print(data)
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("=" * 60)

def get_next_customer_to_call():
    """
    Get the next customer to call from Supabase based on priority.
    
    Priority:
    1. Status = 'active'
    2. Risk level (high > medium > low)
    3. Days overdue (oldest first)
    
    Returns:
        dict: Customer data or None if no customers found
    """
    supabase = get_supabase_client()
    
    try:
        # Get all active customers, ordered by priority
        result = supabase.table('customers') \
            .select('*') \
            .eq('status', 'active') \
            .order('due_date', desc=False) \
            .execute()
        
        if not result.data:
            return None
        
        # Sort by risk level manually (high > medium > low)
        risk_priority = {'high': 1, 'medium': 2, 'low': 3}
        sorted_customers = sorted(
            result.data, 
            key=lambda x: (risk_priority.get(x['risk_level'], 999), x['due_date'])
        )
        
        return sorted_customers[0]
        
    except Exception as e:
        print(f"❌ Error getting customer: {e}")
        return None

if __name__ == "__main__":
    if not ELEVENLABS_API_KEY or not ELEVENLABS_AGENT_ID:
        print("❌ Error: Missing ElevenLabs credentials")
        print("Please set ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID in .env file")
        sys.exit(1)
    
    # Check if specific phone number was provided
    if len(sys.argv) >= 2:
        phone = sys.argv[1]
        
        # Try to get customer from database
        supabase = get_supabase_client()
        result = supabase.table('customers').select('*').eq('phone', phone).execute()
        
        if result.data:
            customer = result.data[0]
            make_call(customer['phone'], customer['name'])
        else:
            # Use provided phone with generic name
            print(f"⚠️  Customer not found in database, calling anyway...")
            make_call(phone, "the account holder")
    else:
        # Auto-select next customer based on priority
        print("📋 Auto-selecting next customer to call based on priority...")
        print()
        
        customer = get_next_customer_to_call()
        
        if customer:
            print(f"Selected: {customer['name']}")
            print(f"  Phone: {customer['phone']}")
            print(f"  Debt: ${customer['debt_amount']}")
            print(f"  Risk: {customer['risk_level']}")
            print(f"  Due date: {customer['due_date']}")
            print()
            
            confirm = input("Proceed with call? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                make_call(customer['phone'], customer['name'])
            else:
                print("❌ Call cancelled")
        else:
            print("❌ No active customers found in database")
            print()
            print("Usage: python make_call.py [phone_number]")
            print()
            print("Examples:")
            print("  python make_call.py                    # Auto-select next customer")
            print("  python make_call.py +15551234567       # Call specific number")

