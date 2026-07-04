import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (useful for local development)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent
