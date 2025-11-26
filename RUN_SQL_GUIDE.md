# Quick Guide: Run SQL in Supabase

## Step 1: Open Supabase SQL Editor

1. Go to: https://supabase.com/dashboard/project/prdfwzvjybtmnqnneuds/sql
2. Log in if needed
3. You should see the SQL Editor interface

## Step 2: Create New Query

1. Click **"New Query"** button (usually top right)
2. A new editor tab will open

## Step 3: Copy and Paste SQL

1. Open the file: `/Users/willianmartinez/voice_agent/schema.sql`
2. Select all (Cmd+A) and copy (Cmd+C)
3. Paste into the Supabase SQL Editor

OR copy this SQL directly:

```sql
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

CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Step 4: Run the SQL

1. Click **"Run"** button (or press Cmd+Enter)
2. You should see success messages
3. The `customers` table is now created!

## Step 5: Verify Table Created

1. In Supabase, go to **Table Editor** (left sidebar)
2. You should see the `customers` table listed
3. Click on it to see the empty table

## ✅ Done!

Once you've run the SQL, come back here and we'll load the test data.
