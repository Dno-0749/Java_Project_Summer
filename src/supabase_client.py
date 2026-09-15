import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_PUBLISHABLE_KEY")
)


def get_supabase_client() -> Client:
    """Return a Supabase client. Accepts both legacy and current env variable names."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and one of SUPABASE_KEY/SUPABASE_SERVICE_ROLE_KEY are required in environment"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)
