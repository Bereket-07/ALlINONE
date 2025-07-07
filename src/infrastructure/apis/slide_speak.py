import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from typing import Optional
from ...config import SLIDESPEAK_API_KEY

# ---- SLIDESPEAK ----
class SlideSpeakInput(BaseModel):
    plain_text: str
    length: int = 6
    theme: str = "default"
    language: str = "ORIGINAL"
    fetch_images: bool = True
    tone: str = "default"
    verbosity: str = "standard"
    custom_user_instructions: Optional[str] = None

def call_slidespeak(**kwargs) -> str:
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": SLIDESPEAK_API_KEY
        }
        resp = requests.post(
            "https://api.slidespeak.co/api/v1/presentation/generate",
            headers=headers,
            json=kwargs,
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()
        return result["task_result"]["url"]
    except Exception as e:
        return f"SlideSpeak API error: {e}"

slidespeak_tool = Tool.from_function(
    func=call_slidespeak,
    name="slidespeak_tool",
    description="Generate a PowerPoint presentation using SlideSpeak.",
    args_schema=SlideSpeakInput,
)