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

class SlideSpeakClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.slidespeak.co/api/v1/presentation/generate"

    def generate_presentation(self, **kwargs) -> str:
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            resp = requests.post(
                self.api_url,
                headers=headers,
                json=kwargs,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
            return result["task_result"]["url"]
        except Exception as e:
            return f"SlideSpeak API error: {e}"

slidespeak_client = SlideSpeakClient(SLIDESPEAK_API_KEY)

def call_slidespeak_tool(input: SlideSpeakInput) -> str:
    return slidespeak_client.generate_presentation(**input.dict())

slidespeak_tool = Tool.from_function(
    func=call_slidespeak_tool,
    name="slidespeak_tool",
    description="Generate a PowerPoint presentation using SlideSpeak.",
    args_schema=SlideSpeakInput,
)