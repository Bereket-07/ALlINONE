import requests
from langchain_core.tools import Tool
from pydantic import BaseModel
from ...config import SIMILARWEB_API_KEY

class SimilarWebInput(BaseModel):
    domain: str
    start_date: str
    end_date: str
    granularity: str = "daily"

class SimilarWebClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.similarweb.com/v1/website/"

    def get_traffic_and_engagement(self, domain: str, start_date: str, end_date: str, granularity: str = "daily") -> str:
        try:
            url = f"{self.base_url}{domain}/traffic-and-engagement"
            headers = {
                "api-key": self.api_key,
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

similarweb_client = SimilarWebClient(SIMILARWEB_API_KEY)

def call_similarweb_tool(input: SimilarWebInput) -> str:
    return similarweb_client.get_traffic_and_engagement(
        domain=input.domain,
        start_date=input.start_date,
        end_date=input.end_date,
        granularity=input.granularity
    )

similarweb_tool = Tool.from_function(
    func=call_similarweb_tool,
    name="similarweb_tool",
    description="Get website traffic and engagement metrics using SimilarWeb",
    args_schema=SimilarWebInput,
)