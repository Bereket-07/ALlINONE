import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from ...config import STABILITY_AI_API_KEY

# ---- STABILITY AI ----
class StabilityAIInput(BaseModel):
    prompt: str
    cfg_scale: int = 7
    height: int = 1024
    width: int = 1024
    samples: int = 1
    steps: int = 30

class StabilityAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    def generate_image(self, prompt: str, cfg_scale: int = 7, height: int = 1024, width: int = 1024, samples: int = 1, steps: int = 30) -> str:
        try:
            data = {
                "text_prompts": [{"text": prompt, "weight": 1}],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": samples,
                "steps": steps
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            resp = requests.post(self.api_url, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json()["artifacts"][0].get("base64", "No image data returned.")
        except Exception as e:
            return f"Stability AI API error: {e}"

stability_client = StabilityAIClient(STABILITY_AI_API_KEY)

def call_stability_ai_tool(input: StabilityAIInput) -> str:
    return stability_client.generate_image(
        prompt=input.prompt,
        cfg_scale=input.cfg_scale,
        height=input.height,
        width=input.width,
        samples=input.samples,
        steps=input.steps
    )

stability_tool = Tool.from_function(
    func=call_stability_ai_tool,
    name="stability_ai_tool",
    description="Generate an image using Stability AI with SDXL",
    args_schema=StabilityAIInput,
)