import httpx
from pydantic import BaseModel
from src.config import RUNWAY_API_KEY
from typing import Optional
from src.infrastructure.llm.llm_interface import LLMInterface

class RunwayInput(BaseModel):
    prompt: str
    model: str = "gen-2"
    duration: int = 4
    width: int = 1280
    height: int = 720

class RunwayClient(LLMInterface):
    """
    Async-compatible Runway video/image generation client.
    Inherits from LLMInterface for compatibility with LLM workflows.
    """
    def __init__(self, api_key: Optional[str] = RUNWAY_API_KEY):
        if not api_key:
            raise ValueError("API key for Runway must be provided.")
        self.api_key = api_key
        self.api_url = "https://api.runwayml.com/v1/generations"

    async def generate_response(self, prompt: str) -> str:
        """
        LLMInterface-compliant method: generate a video/image from a prompt string.
        Uses default model and parameters.
        """
        input = RunwayInput(prompt=prompt)
        return await self.generate_response_from_input(input)

    async def generate_response_from_input(self, input: RunwayInput) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": input.prompt,
            "model": input.model,
            "duration": input.duration,
            "width": input.width,
            "height": input.height
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.api_url, headers=headers, json=data)
                resp.raise_for_status()
                return resp.json().get("output", {}).get("url", "No output URL found.")
        except Exception as e:
            print(f"Runway API error: {e}")
            return f"Error: Could not generate video/image with Runway."

import asyncio

def get_default_client():
    return RunwayClient()

async def main():
    client = get_default_client()
    input_data = RunwayInput(
        prompt="A futuristic cityscape at sunset",
        model="gen-2",
        duration=4,
        width=1280,
        height=720
    )
    # Test both LLMInterface and full input
    result = await client.generate_response(input_data.prompt)
    print("Result (LLMInterface):", result)
    result_full = await client.generate_response_from_input(input_data)
    print("Result (full input):", result_full)

if __name__ == "__main__":
    asyncio.run(main())
