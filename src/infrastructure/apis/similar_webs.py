import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from ...config import SIMILARWEB_API_KEY

class SimilarWebInput(BaseModel):
    domain: str
    start_date: str
    end_date: str
    granularity: str = "daily"

def call_similarweb(domain: str, start_date: str, end_date: str, granularity: str = "daily") -> str:
    try:
        url = f"https://api.similarweb.com/v1/website/{domain}/traffic-and-engagement"
        headers = {
            "api-key": SIMILARWEB_API_KEY,
            "Content-Type": "application/json"
        }
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "granularity": granularity
        }
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return str(resp.json())
    except Exception as e:
        return f"SimilarWeb API error: {e}"

similarweb_tool = Tool.from_function(
    func=call_similarweb,
    name="similarweb_tool",
    description="Get website traffic and engagement metrics using SimilarWeb",
    args_schema=SimilarWebInput,
)