import urllib.parse

base_auth_url = "https://appcenter.intuit.com/connect/oauth2"
params = {
    "client_id": "ABAoUbCJVLtKWncFzy1RQwQtnvFseVi91lObKMfR3MlqTNRrzH",
    "redirect_uri": "http://localhost:8000/callback",
    "response_type": "code",
    "scope": "com.intuit.quickbooks.accounting",  # Add more scopes if needed
    "state": "testState123"  # Optional, but good practice
}
auth_url = base_auth_url + "?" + urllib.parse.urlencode(params)
print(auth_url)
