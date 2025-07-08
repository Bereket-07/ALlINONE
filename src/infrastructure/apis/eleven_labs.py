from elevenlabs.client import ElevenLabs
from elevenlabs import play
from elevenlabs.core.api_error import ApiError
import base64
import json
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
        self.api_key = api_key
        if api_key is None:
            raise ValueError("API key for ElevenLabs must be provided.")
    
    def generate_audio(self, prompt: str):
        
        client = ElevenLabs(api_key=self.api_key)  # Replace with real key

        try:
            audio = client.text_to_speech.convert(
                voice_id="pFZP5JQG7iQjIQuC4Bku",
                model_id="eleven_monolingual_v1",
                text=prompt
            )

            audio_bytes = audio # Collect all bytes from the generator
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            response = {"audio_base64": audio_base64}
            return json.dumps(response)

        except ApiError as e:
            response = {
                "error": "API Error",
                "status_code": e.status_code,
                "message": e.body.get("detail", {}).get("message", "Unknown error")
            }
            return json.dumps(response)
        except Exception as ex:
            response ={
                "error": "Unexpected Error",
                "message": str(ex)
            }
            return json.dumps(response)


# async def main():
#     llm = ElevenLabsLLM()
#     llm.init()  # Uses default ELEVENLABS_API_KEY from config

#     input_data = ElevenLabsInput(
#         voice_id="your_voice_id",  # Replace with a valid voice_id
#         text="Hello, this is a test from ElevenLabsLLM.",
#         model_id="eleven_multilingual_v2",
#         stability=0.5,
#         similarity_boost=0.7
#     )

#     result = await llm.generate_response(input_data)
#     print("Result:", result)

# if __name__ == "__main__":
#     asyncio.run(main())