"""
Database setup script for Jess Voice Agent PoC.
Creates the customers table with proper schema and indexes.
"""

from database import get_supabase_client


def setup_database():
    """
    Creates the customers table in Supabase.
    This script is idempotent - safe to run multiple times.
    """
    supabase = get_supabase_client()
    
    # SQL to create customers table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        phone TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        debt_amount NUMERIC NOT NULL,
        due_date DATE,
        status TEXT DEFAULT 'active',
        risk_level TEXT DEFAULT 'medium',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
    CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
    
    -- Create updated_at trigger function
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    -- Create trigger to auto-update updated_at
    DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
    CREATE TRIGGER update_customers_updated_at
        BEFORE UPDATE ON customers
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        # Execute the SQL using Supabase's RPC or direct SQL execution
        # Note: Supabase Python client doesn't have direct SQL execution
        # You'll need to run this SQL in the Supabase SQL Editor or use PostgREST
        print("📋 Database Setup Instructions:")
        print("=" * 60)
        print("Please run the following SQL in your Supabase SQL Editor:")
        print("=" * 60)
        print(create_table_sql)
        print("=" * 60)
        print("\nAlternatively, you can:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to 'SQL Editor'")
        print("3. Create a new query")
        print("4. Paste the SQL above")
        print("5. Click 'Run'")
        print("\n✅ After running the SQL, your database will be ready!")
        
        # Try to verify if table exists by querying it
        try:
            result = supabase.table('customers').select("*").limit(1).execute()
            print("\n✅ Table 'customers' already exists and is accessible!")
            return True
        except Exception as e:
            print(f"\n⚠️  Table 'customers' not found. Please run the SQL above.")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Jess Voice Agent Database Setup...\n")
    setup_database()
