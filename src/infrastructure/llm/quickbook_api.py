import requests
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class QuickBooksAPI:
    def __init__(self):
        self.access_token = os.getenv("QB_ACCESS_TOKEN")
        self.realm_id = os.getenv("QB_REALM_ID")

        if not self.access_token or not self.realm_id:
            raise EnvironmentError("Missing QB_ACCESS_TOKEN or QB_REALM_ID in .env")

        self.base_url = f"https://quickbooks.api.intuit.com/v3/company/{self.realm_id}/query"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }

    def run_query(self, query: str) -> Optional[Dict]:
        if not query.strip():
            raise ValueError("Query string must not be empty.")

        try:
            response = requests.get(
                url=self.base_url,
                headers=self.headers,
                params={"query": query, "minorversion": "65"}
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error during QuickBooks API request: {e}")
            return None

# Example usage:
# Create a .env file with:
# QB_ACCESS_TOKEN=your_access_token
# QB_REALM_ID=your_realm_id
# qbo = QuickBooksAPI()
# result = qbo.run_query("SELECT * FROM Customer")
# print(result)
