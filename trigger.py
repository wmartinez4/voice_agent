"""
Trigger script for Jess Voice Agent PoC.
Initiates outbound calls using ElevenLabs API.

This script:
1. Queries Supabase for customers with 'active' status
2. Uses ElevenLabs API to start a conversation
3. Passes only the customer phone number as initial context (privacy-first)
"""

import os
import requests
from database import get_supabase_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

if not ELEVENLABS_API_KEY or not ELEVENLABS_AGENT_ID:
    raise ValueError(
        "Missing ElevenLabs credentials. "
        "Please set ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID in your .env file"
    )


def trigger_call(customer_phone: str, customer_name: str):
    """
    Initiates an outbound call to a customer using ElevenLabs Conversational AI API.
    
    Args:
        customer_phone: Customer's phone number (E.164 format, e.g., +15551234567)
        customer_name: Customer's name (for display only)
        
    Returns:
        dict: Response from ElevenLabs API if successful, None otherwise
    """
    print(f"📞 Initiating call to {customer_name} at {customer_phone}...")
    
    # ElevenLabs Conversational AI API endpoint
    url = f"https://api.elevenlabs.io/v1/convai/conversation"
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "agent_id": ELEVENLABS_AGENT_ID,
        "phone_number": customer_phone,
        # Optional: Pass custom variables to the agent
        # "variables": {
        #     "customer_name": customer_name
        # }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        conversation_id = data.get("conversation_id", "unknown")
        
        print(f"✅ Call initiated successfully!")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Customer: {customer_name}")
        print(f"   Phone: {customer_phone}")
        
        return data
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response is not None:
            print(f"   Status Code: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None


def get_customers_to_call(limit: int = 5):
    """
    Retrieves customers with 'active' status from database.
    
    Args:
        limit: Maximum number of customers to retrieve
        
    Returns:
        List of customer records
    """
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('customers').select("*").eq('status', 'active').limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"❌ Error retrieving customers: {e}")
        return []


def main():
    """
    Main function to trigger calls for active customers.
    """
    print("=" * 60)
    print("🚀 Jess Voice Agent - Call Trigger")
    print("=" * 60)
    print()
    
    # Get customers to call
    customers = get_customers_to_call(limit=5)
    
    if not customers:
        print("⚠️  No active customers found to call.")
        return
    
    print(f"📋 Found {len(customers)} active customer(s):\n")
    
    for i, customer in enumerate(customers, 1):
        print(f"{i}. {customer['name']} - {customer['phone']} - ${customer['debt_amount']}")
    
    print("\n" + "=" * 60)
    
    # Ask user which customer to call
    choice = input("\nEnter customer number to call (or 'all' for all, 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("👋 Exiting...")
        return
    
    if choice == 'all':
        # Call all customers
        for customer in customers:
            trigger_call(customer['phone'], customer['name'])
            print()
    else:
        # Call specific customer
        try:
            index = int(choice) - 1
            if 0 <= index < len(customers):
                customer = customers[index]
                trigger_call(customer['phone'], customer['name'])
            else:
                print("❌ Invalid customer number")
        except ValueError:
            print("❌ Invalid input")
    
    print("\n" + "=" * 60)
    print("✅ Trigger script completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT NOTES:")
    print("=" * 60)
    print("1. This script requires ElevenLabs SDK configuration")
    print("2. Make sure your ElevenLabs agent is properly set up")
    print("3. Ensure Twilio is connected to your ElevenLabs account")
    print("4. Test with a single customer first before calling all")
    print("5. The actual SDK method may need adjustment based on")
    print("   the ElevenLabs Python SDK version you're using")
    print("=" * 60)
    print()
    
    confirm = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        main()
    else:
        print("👋 Cancelled.")
