import os
from typing import Optional

try:
    from supabase import create_client, Client
except Exception:  # supabase-py not installed yet
    create_client = None
    Client = None


def get_supabase_client() -> Optional["Client"]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key or create_client is None:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

