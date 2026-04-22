"""Thin Supabase client wrapper for the Flask app.

Set SUPABASE_URL and SUPABASE_SERVICE_KEY env vars to activate.
When not configured, get_supabase() returns None and callers should fall back
to the local SQLite implementation.
"""
import os
from functools import lru_cache

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None


SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')


def is_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY and create_client is not None)


@lru_cache(maxsize=1)
def get_supabase():
    """Return a cached Supabase client, or None if env vars are missing."""
    if not is_configured():
        return None
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
