import os
from typing import Dict, Optional

import requests


class CanvasAPI:
    def __init__(self):
        self.api_key = os.getenv("CANVAS_API_KEY")
        self.base_url = os.getenv("CANVAS_API_URL")

        if not self.api_key or not self.base_url:
            raise EnvironmentError("Missing CANVAS_API_KEY or CANVAS_API_URL in .env")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def run_query(self, query: str) -> Optional[Dict]:
        if not query.strip():
            raise ValueError("Query string must not be empty.")

        try:
            response = requests.post(
                url=f"{self.base_url}/query",
                headers=self.headers,
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error during Canvas API request: {e}")
            return None