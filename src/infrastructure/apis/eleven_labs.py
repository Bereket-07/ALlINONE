import httpx
from pydantic import BaseModel
from src.config import ELEVENLABS_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface



class ElevenLabsInput(BaseModel):
    voice_id: str
    text: str
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.5
    similarity_boost: float = 0.7


class ElevenLabsLLM(LLMInterface):
    """
    Async-compatible ElevenLabs TTS (Text-to-Speech) wrapper.
    """

    def __init__(self, api_key: str = ELEVENLABS_API_KEY):
        if api_key is None:
            raise ValueError("API key for ElevenLabs must be provided.")
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1/models"

    async def generate_response(self, input: ElevenLabsInput) -> str:
        """
        Converts text to speech using ElevenLabs API.
        Returns a URL to the audio or a base64 audio string (if supported).
        """
        url = f"{self.base_url}{input.voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "text": input.text,
            "model_id": input.model_id,
            "voice_settings": {
                "stability": input.stability,
                "similarity_boost": input.similarity_boost
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()

                # ElevenLabs may return audio as binary or a link
                # If binary: return base64 or save to file
                # If JSON: return audio field
                if response.headers.get("Content-Type") == "application/json":
                    return response.json().get("audio", "No audio returned.")
                else:
                    return "Audio response received (non-JSON). Handle accordingly."

        except Exception as e:
            print(f"ElevenLabs API error: {e}")
            return "Error: Could not generate audio with ElevenLabs."


import asyncio
# from src.infrastructure.apis.eleven_labs import ElevenLabsLLM, ElevenLabsInput

async def main():
    llm = ElevenLabsLLM()
    llm.init()  # Uses default ELEVENLABS_API_KEY from config

    input_data = ElevenLabsInput(
        voice_id="your_voice_id",  # Replace with a valid voice_id
        text="Hello, this is a test from ElevenLabsLLM.",
        model_id="eleven_multilingual_v2",
        stability=0.5,
        similarity_boost=0.7
    )

    result = await llm.generate_response(input_data)
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())