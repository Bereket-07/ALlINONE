import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from ...config import RUNWAY_API_KEY

# ---- RUNWAY ----
class RunwayInput(BaseModel):
    prompt: str
    model: str = "gen-2"
    duration: int = 4
    width: int = 1280
    height: int = 720

class RunwayClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.runwayml.com/v1/generations"

    def generate(self, prompt: str, model: str = "gen-2", duration: int = 4, width: int = 1280, height: int = 720) -> str:
        try:
            data = {
                "prompt": prompt,
                "model": model,
                "duration": duration,
                "width": width,
                "height": height
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            resp = requests.post(self.api_url, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json().get("output", {}).get("url", "No output URL found.")
        except Exception as e:
            return f"Runway API error: {e}"

runway_client = RunwayClient(RUNWAY_API_KEY)

def call_runway_tool(input: RunwayInput) -> str:
    return runway_client.generate(
        prompt=input.prompt,
        model=input.model,
        duration=input.duration,
        width=input.width,
        height=input.height
    )

runway_tool = Tool.from_function(
    func=call_runway_tool,
    name="runway_tool",
    description="Generate video/image from prompt using Runway",
    args_schema=RunwayInput,
)
