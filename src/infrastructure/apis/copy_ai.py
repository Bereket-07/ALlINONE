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

def call_copy_ai(prompt: str, max_tokens: int = 200, tone: str = "friendly", language: str = "en") -> str:
    try:
        resp = requests.post(
            "https://api.copy.ai/v1/completions",
            headers={
                "Authorization": f"Bearer {COPY_AI_API_KEY}",
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

copy_ai_tool = Tool.from_function(
    func=call_copy_ai,
    name="copy_ai_tool",
    description="Use Copy.ai to generate content from a prompt",
    args_schema=CopyAIInput,
)