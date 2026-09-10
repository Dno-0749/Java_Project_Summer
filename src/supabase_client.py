import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Return the privileged backend client; never expose its key to the frontend."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment")
    return create_client(url, key)
