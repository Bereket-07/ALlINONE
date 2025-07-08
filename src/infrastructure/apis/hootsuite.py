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

class HootsuiteClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api_url = "https://api.hootsuite.com/v2/posts"

    def schedule_post(self, text: str, socialProfileIds: List[str], scheduledSendTime: str) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "socialProfileIds": socialProfileIds,
                "scheduledSendTime": scheduledSendTime
            }
            resp = requests.post(self.api_url, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json().get("id", "No post ID returned.")
        except Exception as e:
            return f"Hootsuite API error: {e}"

hootsuite_client = HootsuiteClient(HOOTSUITE_ACCESS_TOKEN)

def call_hootsuite_tool(input: HootsuiteInput) -> str:
    return hootsuite_client.schedule_post(
        text=input.text,
        socialProfileIds=input.socialProfileIds,
        scheduledSendTime=input.scheduledSendTime
    )

hootsuite_tool = Tool.from_function(
    func=call_hootsuite_tool,
    name="hootsuite_tool",
    description="Schedule a social media post using Hootsuite API",
    args_schema=HootsuiteInput,
)
