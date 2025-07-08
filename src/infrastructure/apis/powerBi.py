import requests
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from typing import List
from ...config import POWERBI_ACCESS_TOKEN

# ---- POWER BI ----
class PowerBIInput(BaseModel):
    datasetId: str
    name: str
    visualizations: List[dict]
    access_token: str = Field(..., description="OAuth2 access token")

class PowerBIClient:
    def __init__(self):
        self.api_url = "https://api.powerbi.com/v1.0/myorg/reports"

    def create_report(self, datasetId: str, name: str, visualizations: List[dict], access_token: str) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "datasetId": datasetId,
                "name": name,
                "visualizations": visualizations
            }
            resp = requests.post(self.api_url, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json().get("webUrl", "No web URL returned.")
        except Exception as e:
            return f"Power BI API error: {e}"

powerbi_client = PowerBIClient()

def call_powerbi_tool(input: PowerBIInput) -> str:
    return powerbi_client.create_report(
        datasetId=input.datasetId,
        name=input.name,
        visualizations=input.visualizations,
        access_token=input.access_token
    )

powerbi_tool = Tool.from_function(
    func=call_powerbi_tool,
    name="powerbi_tool",
    description="Create a Power BI report using dataset and visualization specs",
    args_schema=PowerBIInput,
)