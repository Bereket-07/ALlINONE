import httpx
from pydantic import BaseModel
from src.config import STABILITY_AI_API_KEY
from typing import Optional
from src.infrastructure.llm.llm_interface import LLMInterface


class StabilityAIInput(BaseModel):
    prompt: str
    cfg_scale: int = 7
    height: int = 1024
    width: int = 1024
    samples: int = 1
    steps: int = 30

class StabilityAIClient(LLMInterface):
    """
    Async-compatible Stability AI image generation client.
    Inherits from LLMInterface for compatibility with LLM workflows.
    """
    def __init__(self, api_key: Optional[str] = STABILITY_AI_API_KEY):
        if not api_key:
            raise ValueError("API key for Stability AI must be provided.")
        self.api_key = api_key
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    async def generate_response(self, prompt: str , history: str) -> str:
        """
        LLMInterface-compliant method: generate an image from a prompt string using default parameters.
        """
        input = StabilityAIInput(prompt=prompt)
        return await self.generate_response_from_input(input)

    async def generate_response_from_input(self, input: StabilityAIInput) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "text_prompts": [{"text": input.prompt, "weight": 1}],
            "cfg_scale": input.cfg_scale,
            "height": input.height,
            "width": input.width,
            "samples": input.samples,
            "steps": input.steps
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.api_url, headers=headers, json=data)
                print(resp)
                resp.raise_for_status()
                return resp.json()["artifacts"][0].get("base64", "No image data returned.")
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                print("Stability AI API error:", e.response.text)
            else:
                print(f"Stability AI API error: {e}")
            return f"Error: Could not generate image with Stability AI."

