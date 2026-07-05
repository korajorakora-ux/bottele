import logging
import asyncio
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
else:
    logger.warning("SUPABASE_URL or SUPABASE_KEY not found. Database features will be disabled.")

async def upsert_user(user_id: int, first_name: str, username: str):
    """Inserts or updates a user in the Supabase database asynchronously."""
    if not supabase:
        return
        
    try:
        data = {
            "user_id": user_id,
            "first_name": first_name or "",
            "username": username or ""
        }
        
        loop = asyncio.get_event_loop()
        # Using run_in_executor to avoid blocking the async event loop with synchronous HTTP requests
        await loop.run_in_executor(
            None, 
            lambda: supabase.table("telegram_users").upsert(data).execute()
        )
        logger.info(f"User {user_id} saved to Supabase.")
    except Exception as e:
        logger.error(f"Error saving user {user_id} to Supabase: {e}")

async def get_all_users() -> list[int]:
    """Fetches all user_ids from the Supabase database asynchronously."""
    if not supabase:
        return []
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: supabase.table("telegram_users").select("user_id").execute()
        )
        return [row["user_id"] for row in response.data]
    except Exception as e:
        logger.error(f"Error fetching users from Supabase: {e}")
        return []
