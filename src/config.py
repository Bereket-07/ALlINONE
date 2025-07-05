import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- New API Keys ---
ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
STABILITY_AI_API_KEY = os.getenv("STABILITY_AI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
TAVUS_API_KEY = os.getenv("TAVUS_API_KEY")
CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")
PELTARION_API_KEY = os.getenv("PELTARION_API_KEY")
SYNTHESIS_AI_API_KEY = os.getenv("SYNTHESIS_AI_API_KEY")
LUMEN_API_KEY = os.getenv("LUMEN_API_KEY")
IMAGGA_API_KEY = os.getenv("IMAGGA_API_KEY")
KENTOSH_API_KEY = os.getenv("KENTOSH_API_KEY")
ZENI_API_KEY = os.getenv("ZENI_API_KEY")

# --- API Base URLs ---
ASSEMBLY_AI_BASE_URL = "https://api.assemblyai.com/v2"
STABILITY_AI_BASE_URL = "https://api.stability.ai/v1"
ELEVEN_LABS_BASE_URL = "https://api.elevenlabs.io/v1"
GOOGLE_VISION_BASE_URL = "https://vision.googleapis.com/v1"
GOOGLE_TRANSLATE_BASE_URL = "https://translation.googleapis.com/language/translate/v2"
TAVUS_BASE_URL = "https://api.tavus.com/v1"
CLARIFAI_BASE_URL = "https://api.clarifai.com/v2"
PELTARION_BASE_URL = "https://api.peltarion.com/v1"
SYNTHESIS_AI_BASE_URL = "https://api.synthesis.ai/v1"
LUMEN_BASE_URL = "https://api.lumen.com/v1"
IMAGGA_BASE_URL = "https://api.imagga.com/v2"
KENTOSH_BASE_URL = "https://api.kentosh.com/v1"
ZENI_BASE_URL = "https://api.zeni.com/v1"

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