import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from typing import List
from ...config import HOOTSUITE_ACCESS_TOKEN

# ---- HOOTSUITE ----
class HootsuiteInput(BaseModel):
    text: str
    socialProfileIds: List[str]
    scheduledSendTime: str

def call_hootsuite(text: str, socialProfileIds: List[str], scheduledSendTime: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {HOOTSUITE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "socialProfileIds": socialProfileIds,
            "scheduledSendTime": scheduledSendTime
        }
        resp = requests.post("https://api.hootsuite.com/v2/posts", headers=headers, json=data)
        resp.raise_for_status()
        return resp.json().get("id", "No post ID returned.")
    except Exception as e:
        return f"Hootsuite API error: {e}"

hootsuite_tool = Tool.from_function(
    func=call_hootsuite,
    name="hootsuite_tool",
    description="Schedule a social media post using Hootsuite API",
    args_schema=HootsuiteInput,
)
