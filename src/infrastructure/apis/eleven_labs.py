from elevenlabs.client import ElevenLabs
from elevenlabs import play
from elevenlabs.core.api_error import ApiError
import base64
import json
from pydantic import BaseModel
from src.config import ELEVENLABS_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface
from typing import Optional


class ElevenLabsInput(BaseModel):
    text: str
    voice_id: str = "pFZP5JQG7iQjIQuC4Bku"
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.5
    similarity_boost: float = 0.7


class ElevenLabsLLM(LLMInterface):
    """
    Async-compatible ElevenLabs TTS (Text-to-Speech) wrapper.
    """

    def __init__(self, api_key: Optional[str] = ELEVENLABS_API_KEY):
        if not api_key:
            raise ValueError("API key for ElevenLabs must be provided.")
        self.api_key = api_key
    
    def generate_response(self, input_data: ElevenLabsInput):
        
        client = ElevenLabs(api_key=self.api_key)
        try:
            audio = client.text_to_speech.convert(
                voice_id=input_data.voice_id,
                model_id=input_data.model_id,
                text=input_data.text
            )
            audio_bytes = b"".join(audio)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            response = {"audio_base64": audio_base64}
            return json.dumps(response)
        except ApiError as e:
            response = {
                "error": "API Error",
                "status_code": getattr(e, 'status_code', None),
                "message": str(e.body)
            }
            return json.dumps(response)
        except Exception as ex:
            response = {
                "error": "Unexpected Error",
                "message": str(ex)
            }
            return json.dumps(response)


def main():
    llm = ElevenLabsLLM()

    input_data = ElevenLabsInput(
        text="Hello, this is a test from ElevenLabsLLM.",
    )

    result = llm.generate_response(input_data)
    print("Result:", result)

if __name__ == "__main__":
    main()