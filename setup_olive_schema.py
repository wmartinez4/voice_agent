
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Error: Missing Supabase credentials")
    exit(1)

supabase: Client = create_client(url, key)

# SQL to add new columns if they don't exist
# Note: Supabase-py client doesn't support direct DDL via table() methods easily without SQL editor access usually,
# but we can try using rpc() if a function exists, or just print instructions.
# However, for this environment, we assume we might NOT have direct DDL access from python if not owner.
# We will TRY to just insert and let Supabase functionality handle it if columns exist, 
# BUT since I cannot run SQL migrations easily from here without the dashboard,
# I will assume the table structure needs to be compatible.

# ACTUALLY: The best way to mock this if we can't alter schema is to store extra data in a 'meta' jsonb column if it existed,
# or just fail.
# Let's try to query a non-existent column to check.

print("⚠️ Note: Please ensure the 'customers' table in Supabase has the following columns:")
print("- vehicle (text)")
print("- auto_renew (boolean)")
print("- policy_number (text)")
print("\nIf not, run this SQL in your Supabase SQL Editor:")
print("""
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS vehicle text,
ADD COLUMN IF NOT EXISTS auto_renew boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS policy_number text;
""")

# We will try to run the seed script directly. If it fails, the user needs to add columns.
