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

def call_powerbi(datasetId: str, name: str, visualizations: List[dict], access_token: str) -> str:
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
        url = "https://api.powerbi.com/v1.0/myorg/reports"
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json().get("webUrl", "No web URL returned.")
    except Exception as e:
        return f"Power BI API error: {e}"

powerbi_tool = Tool.from_function(
    func=call_powerbi,
    name="powerbi_tool",
    description="Create a Power BI report using dataset and visualization specs",
    args_schema=PowerBIInput,
)