
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    print("❌ Error: ELEVENLABS_API_KEY not found in environment.")
    exit(1)

def list_agents():
    url = "https://api.elevenlabs.io/v1/convai/agents"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"✅ Found {len(agents)} agents:")
            print("-" * 40)
            
            for agent in agents:
                print(f"Name: {agent.get('name')}")
                print(f"ID:   {agent.get('agent_id')}")
                print("-" * 40)
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    list_agents()
