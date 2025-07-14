import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from typing import Optional
from ...config import COPY_AI_API_KEY

# ---- COPY.AI ----
class CopyAIInput(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 200
    tone: Optional[str] = "friendly"
    language: Optional[str] = "en"

class CopyAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.copy.ai/v1/completions"

    def generate(self, prompt: str, max_tokens: int = 200, tone: str = "friendly", language: str = "en") -> str:
        try:
            resp = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "tone": tone,
                    "language": language
                },
                timeout=15
            )
            resp.raise_for_status()
            return resp.json().get("text", "No result returned.")
        except Exception as e:
            return f"Copy.ai API error: {e}"

copy_ai_client = CopyAIClient(COPY_AI_API_KEY)

def call_copy_ai_tool(input: CopyAIInput) -> str:
    return copy_ai_client.generate(
        prompt=input.prompt,
        max_tokens=input.max_tokens,
        tone=input.tone,
        language=input.language
    )

copy_ai_tool = Tool.from_function(
    func=call_copy_ai_tool,
    name="copy_ai_tool",
    description="Use Copy.ai to generate content from a prompt",
    args_schema=CopyAIInput,
)