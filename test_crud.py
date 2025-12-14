import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/customers"

def test_crud():
    print("🧪 Testing CRUD Operations...")
    
    # 1. CREATE
    print("\n1. Testing CREATE (POST)...")
    new_customer = {
        "name": "CRUD Test User",
        "phone": "+18887776666",
        "debt_amount": 123.45,
        "due_date": "2025-12-31",
        "status": "active",
        "risk_level": "low"
    }
    try:
        res = requests.post(BASE_URL, json=new_customer)
        if res.status_code == 200:
            print("✅ Create Success!")
            created_user = res.json().get('customer')
            print(created_user)
            user_id = created_user['id']
        else:
            print(f"❌ Create Failed: {res.status_code} {res.text}")
            return
    except Exception as e:
        print(f"❌ Exception during Create: {e}")
        return

    # 2. UPDATE
    print(f"\n2. Testing UPDATE (PUT) for ID {user_id}...")
    update_data = {"name": "CRUD Test User Updated", "risk_level": "high"}
    try:
        res = requests.put(f"{BASE_URL}/{user_id}", json=update_data)
        if res.status_code == 200:
            print("✅ Update Success!")
            print(res.json().get('customer'))
        else:
            print(f"❌ Update Failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"❌ Exception during Update: {e}")

    # 3. DELETE
    print(f"\n3. Testing DELETE (DELETE) for ID {user_id}...")
    try:
        res = requests.delete(f"{BASE_URL}/{user_id}")
        if res.status_code == 200:
            print("✅ Delete Success!")
        else:
            print(f"❌ Delete Failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"❌ Exception during Delete: {e}")

if __name__ == "__main__":
    test_crud()
