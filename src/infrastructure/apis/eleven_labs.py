import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from ...config import ELEVENLABS_API_KEY

# ---- ELEVENLABS ----
class ElevenLabsInput(BaseModel):
    voice_id: str
    text: str
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.5
    similarity_boost: float = 0.7

def call_elevenlabs(voice_id: str, text: str, model_id: str = "eleven_multilingual_v2", stability: float = 0.5, similarity_boost: float = 0.7) -> str:
    try:
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json().get("audio", "No audio returned.")
    except Exception as e:
        return f"ElevenLabs API error: {e}"

elevenlabs_tool = Tool.from_function(
    func=call_elevenlabs,
    name="elevenlabs_tool",
    description="Convert text to speech using ElevenLabs voice API",
    args_schema=ElevenLabsInput,
)
