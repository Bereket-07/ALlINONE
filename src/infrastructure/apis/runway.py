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

def call_runway(prompt: str, model: str = "gen-2", duration: int = 4, width: int = 1280, height: int = 720) -> str:
    try:
        data = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "width": width,
            "height": height
        }
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json"
        }
        resp = requests.post("https://api.runwayml.com/v1/generations", headers=headers, json=data)
        resp.raise_for_status()
        return resp.json().get("output", {}).get("url", "No output URL found.")
    except Exception as e:
        return f"Runway API error: {e}"

runway_tool = Tool.from_function(
    func=call_runway,
    name="runway_tool",
    description="Generate video/image from prompt using Runway",
    args_schema=RunwayInput,
)
