import asyncio
import traceback
import httpx
import json
import time
import os
from typing import Optional, Union
from pydantic import BaseModel
from src.config import STABILITY_AI_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class StabilityAIInput(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    aspect_ratio: Optional[str] = "1:1"
    seed: Optional[int] = 0
    style_preset: Optional[str] = None
    output_format: Optional[str] = "jpeg"
    image: Optional[str] = None  # Path to image file
    mask: Optional[str] = None   # Path to mask file

class StabilityAIResult(BaseModel):
    image_bytes: Optional[bytes] = None
    finish_reason: Optional[str] = None
    seed: Optional[str] = None
    error: Optional[str] = None

class StabilityAIClient(LLMInterface):
    """
    Async-compatible Stability AI image generation client (v2beta/ultra).
    Inherits from LLMInterface for compatibility with LLM workflows.
    """
    def __init__(self, api_key: Optional[str] = STABILITY_AI_API_KEY):
        if not api_key:
            raise ValueError("API key for Stability AI must be provided.")
        self.api_key = api_key
        self.api_url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

    async def generate_response(self, prompt: str) -> str:
        input = StabilityAIInput(prompt=prompt)
        result = await self.generate_response_from_input(input)
        if result.error:
            return json.dumps({"error": result.error})
        # Return image as base64 for compatibility
        import base64
        return base64.b64encode(result.image_bytes).decode("utf-8") if result.image_bytes else json.dumps({"error": "No image returned"})

    async def generate_response_from_input(self, input: StabilityAIInput) -> StabilityAIResult:
        headers = {
            "Accept": "image/*",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "prompt": input.prompt,
            "output_format": input.output_format or "jpeg",
            "aspect_ratio": input.aspect_ratio or "1:1",
            "seed": str(input.seed or 0)
        }
        if input.negative_prompt:
            data["negative_prompt"] = input.negative_prompt
        if input.style_preset and input.style_preset != "None":
            data["style_preset"] = input.style_preset
        files = {}
        if input.image:
            files["image"] = open(input.image, "rb")
        if input.mask:
            files["mask"] = open(input.mask, "rb")
        if not files:
            files["none"] = ('', b'')
        try:
            timeout = httpx.Timeout(120.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(self.api_url, headers=headers, files=files,data=data)
                for f in files.values():
                    if hasattr(f, 'close'):
                        f.close()
                if not resp.is_success:
                    return StabilityAIResult(error=f"HTTP {resp.status_code}: {resp.text}")
                    
                image_bytes = resp.content
                finish_reason = resp.headers.get("finish-reason")
                seed = resp.headers.get("seed")
                if finish_reason == 'CONTENT_FILTERED':
                    return StabilityAIResult(error="Generation failed NSFW classifier", finish_reason=finish_reason, seed=seed)
                return StabilityAIResult(image_bytes=image_bytes, finish_reason=finish_reason, seed=seed)
        except Exception as e:
            print("Exception type:", type(e))
            print("Exception args:", e.args)
            traceback.print_exc()
            return StabilityAIResult(error=f"Stability AI API error: {repr(e)}")


# async def main():
#     client = StabilityAIClient()
#     input_data = StabilityAIInput(
#         prompt="A fantasy landscape with mountains and rivers",
#     )

#     result = await client.generate_response_from_input(input_data)
#     if result.error:
#         print("Error:", result.error)
#     else:
#         filename = f"generated_{result.seed}.{input_data.output_format}"
#         if result.image_bytes is not None:
#             with open(filename, "wb") as f:
#                 f.write(result.image_bytes)
#             print(f"Saved image {filename}")
#         else:
#             print("No image bytes to save.")
#         print("Finish reason:", result.finish_reason)
#         print("Seed:", result.seed)

# if __name__ == "__main__":
#     asyncio.run(main())