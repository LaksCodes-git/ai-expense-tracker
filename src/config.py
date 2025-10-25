"""
Configuration file - handles all paths and environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (parent of 'src')
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Load environment variables
load_dotenv(PROJECT_ROOT / '.env')

# File paths (all absolute)
CREDENTIALS_PATH = PROJECT_ROOT / 'credentials' / 'service_account.json'
RECEIPTS_DIR = PROJECT_ROOT / 'receipts'

# Add after CREDENTIALS_PATH line:
GMAIL_CREDENTIALS_PATH = PROJECT_ROOT / 'credentials' / 'gmail_credentials.json'
GMAIL_TOKEN_PATH = PROJECT_ROOT / 'credentials' / 'gmail_token.json'

# Add after the existing verification:
if not GMAIL_CREDENTIALS_PATH.exists():
    print(f"⚠️  WARNING: Gmail credentials not found at: {GMAIL_CREDENTIALS_PATH}")
    print(f"💡 You'll need this for email monitoring (Day 3)")
    
# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# Verify critical files exist
if not CREDENTIALS_PATH.exists():
    raise FileNotFoundError(
        f"❌ Google credentials not found at: {CREDENTIALS_PATH}\n"
        f"💡 Make sure you downloaded the JSON file and saved it as:\n"
        f"   {CREDENTIALS_PATH}"
    )

# Print config on import (for debugging)
if __name__ == "__main__":
    print("📁 Project Configuration:")
    print(f"  Root: {PROJECT_ROOT}")
    print(f"  Credentials: {CREDENTIALS_PATH}")
    print(f"  Receipts: {RECEIPTS_DIR}")
    print(f"  Sheet ID: {GOOGLE_SHEET_ID}")