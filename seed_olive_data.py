
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env vars
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Error: Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(url, key)

# Real data for Next 30 Days (Forecast)
# Including specific high-value targets provided by user
customers = [
    # Immediate Risk (Next 30 Days)
    {
        "name": "Andrew Gioia",
        "phone": "+15550100010", 
        "vehicle": "2017 Ford FUSION",
        "debt_amount": 270.00, # Commission
        "due_date": "2025-12-30",
        "status": "active",
        "risk_level": "high",
        "auto_renew": False,
        "policy_number": "OVSCU.800030090.01"
    },
    {
        "name": "Glory Falls",
        "phone": "+15550100011",
        "vehicle": "2018 Ford EDGE",
        "debt_amount": 269.99,
        "due_date": "2025-12-30",
        "status": "active",
        "risk_level": "high",
        "auto_renew": False,
        "policy_number": "OVSCU.800029611.01"
    },
    {
        "name": "Steven Buchanan",
        "phone": "+15550100012",
        "vehicle": "2016 Ford F150",
        "debt_amount": 248.47,
        "due_date": "2025-12-30",
        "status": "active",
        "risk_level": "medium",
        "auto_renew": False,
        "policy_number": "OVSCU.800017544.02"
    },
    {
        "name": "Gregory Smith",
        "phone": "+15550100013",
        "vehicle": "2018 Ford ESCAPE",
        "debt_amount": 270.01,
        "due_date": "2025-12-30",
        "status": "active",
        "risk_level": "medium",
        "auto_renew": False,
        "policy_number": "EXPVSCU.800030066.01"
    },
    {
        "name": "Franklin Taylor",
        "phone": "+15550100014", 
        "vehicle": "2018 Ford F150",
        "debt_amount": 741.30, # High Value
        "due_date": "2025-12-30",
        "status": "active",
        "risk_level": "critical",
        "auto_renew": False,
        "policy_number": "EXPVSCU.800030062.01"
    },
    {
        "name": "Albert Thomas",
        "phone": "+15550100015",
        "vehicle": "2015 Ford F-150",
        "debt_amount": 431.35,
        "due_date": "2025-12-30",
        "status": "active",
        "risk_level": "high",
        "auto_renew": False,
        "policy_number": "EXPVSCU.800030027.01"
    },
    # Previous Sample Data (Legacy for context if needed)
    {
        "name": "Larry Stout",
        "phone": "+15550100001",
        "vehicle": "2013 Ford F150",
        "debt_amount": 164.79,
        "due_date": "2024-12-27",
        "status": "active",
        "risk_level": "medium",
        "auto_renew": False,
        "policy_number": "CVSCSP.800000321.07"
    }
]

print(f"🚀 Seeding {len(customers)} real customer records from 30-Day Forecast...")

for customer in customers:
    try:
        # Check if exists
        existing = supabase.table("customers").select("id").eq("phone", customer["phone"]).execute()
        
        if existing.data:
            print(f"🔄 Updating {customer['name']}...")
            supabase.table("customers").update(customer).eq("id", existing.data[0]['id']).execute()
        else:
            print(f"✨ Creating {customer['name']}...")
            supabase.table("customers").insert(customer).execute()
            
    except Exception as e:
        print(f"❌ Error processing {customer['name']}: {e}")

print("✅ Seeding complete!")
