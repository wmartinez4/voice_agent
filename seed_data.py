"""
Seed data script for Jess Voice Agent PoC.
Creates sample customers with realistic debt scenarios for testing.
"""

from database import get_supabase_client
from datetime import datetime, timedelta


def seed_test_data():
    """
    Inserts sample customer data into the database.
    """
    supabase = get_supabase_client()
    
    # Sample customers with different scenarios
    test_customers = [
        {
            "phone": "+15551234567",
            "name": "María González",
            "debt_amount": 500.00,
            "due_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "status": "active",
            "risk_level": "medium"
        },
        {
            "phone": "+15559876543",
            "name": "Carlos Rodríguez",
            "debt_amount": 1200.00,
            "due_date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
            "status": "active",
            "risk_level": "high"
        },
        {
            "phone": "+15555555555",
            "name": "Ana Martínez",
            "debt_amount": 250.00,
            "due_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "active",
            "risk_level": "low"
        }
    ]
    
    print("🌱 Seeding test data...\n")
    
    for customer in test_customers:
        try:
            # Try to insert, skip if already exists
            result = supabase.table('customers').insert(customer).execute()
            print(f"✅ Created customer: {customer['name']} ({customer['phone']})")
            print(f"   Debt: ${customer['debt_amount']} | Due: {customer['due_date']}")
        except Exception as e:
            # Check if it's a duplicate key error
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                print(f"⚠️  Customer {customer['name']} already exists, skipping...")
            else:
                print(f"❌ Error inserting {customer['name']}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Database seeding complete!")
    print("=" * 60)
    
    # Display all customers
    try:
        all_customers = supabase.table('customers').select("*").execute()
        print(f"\n📋 Total customers in database: {len(all_customers.data)}")
        print("\nCustomer List:")
        for customer in all_customers.data:
            print(f"  • {customer['name']} - {customer['phone']} - ${customer['debt_amount']} - {customer['status']}")
    except Exception as e:
        print(f"⚠️  Could not retrieve customer list: {e}")


if __name__ == "__main__":
    print("🚀 Starting Jess Voice Agent Data Seeding...\n")
    seed_test_data()
