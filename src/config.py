import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- Third-party API Keys ---
COPY_AI_API_KEY = os.getenv("COPY_AI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
STABILITY_AI_API_KEY = os.getenv("STABILITY_AI_API_KEY")
HOOTSUITE_ACCESS_TOKEN = os.getenv("HOOTSUITE_ACCESS_TOKEN")
POWERBI_ACCESS_TOKEN = os.getenv("POWERBI_ACCESS_TOKEN")
SLIDESPEAK_API_KEY = os.getenv("SLIDESPEAK_API_KEY")
SIMILARWEB_API_KEY = os.getenv("SIMILARWEB_API_KEY")
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")

# --- JWT Configuration ---
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")

# --- Firestore Configuration ---
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

# --- Validation ---
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")
if not FIREBASE_CREDENTIALS_PATH:
    raise ValueError("FIREBASE_CREDENTIALS_PATH is required for Firestore user storage.")