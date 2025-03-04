import requests
import sys
import os

scarf_token = os.environ.get("SCARF_AUTH_TOKEN", "defaulttoken")

headers = {
    "Authorization": f"Bearer {scarf_token}",
    "Content-Encoding": "gzip"
}

# URL for the API endpoint
scarf_import_url = "https://api.scarf.sh/v2/<username or organization name>/import"

response = requests.post(scarf_import_url, headers=headers, data=sys.stdin.buffer)

print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Response: {response.text}")
