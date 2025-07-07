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

class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech/"

    def text_to_speech(self, voice_id: str, text: str, model_id: str = "eleven_multilingual_v2", stability: float = 0.5, similarity_boost: float = 0.7) -> str:
        try:
            headers = {
                "xi-api-key": self.api_key,
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
            url = f"{self.base_url}{voice_id}"
            resp = requests.post(url, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json().get("audio", "No audio returned.")
        except Exception as e:
            return f"ElevenLabs API error: {e}"

elevenlabs_client = ElevenLabsClient(ELEVENLABS_API_KEY)

def call_elevenlabs_tool(input: ElevenLabsInput) -> str:
    return elevenlabs_client.text_to_speech(
        voice_id=input.voice_id,
        text=input.text,
        model_id=input.model_id,
        stability=input.stability,
        similarity_boost=input.similarity_boost
    )

elevenlabs_tool = Tool.from_function(
    func=call_elevenlabs_tool,
    name="elevenlabs_tool",
    description="Convert text to speech using ElevenLabs voice API",
    args_schema=ElevenLabsInput,
)
