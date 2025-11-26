"""
Database connection module for Olivia Voice Agent PoC.
Handles Supabase client initialization and provides reusable connection.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing required environment variables. "
        "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file."
    )

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}")
    raise


def get_supabase_client() -> Client:
    """
    Returns the initialized Supabase client.
    
    Returns:
        Client: Supabase client instance
    """
    return supabase
