import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("PHOENIX_API_KEY")
endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")

print(f"--- Debugging Connection ---")
if not api_key:
    print("❌ ERROR: PHOENIX_API_KEY is MISSING from .env file!")
else:
    print(f"✅ API Key found. Length: {len(api_key)} characters.")
    print(f"Key starts with: {api_key[:5]}... and ends with ...{api_key[-5:]}")

if not endpoint:
    print("❌ ERROR: PHOENIX_COLLECTOR_ENDPOINT is MISSING from .env file!")
else:
    print(f"✅ Endpoint found: {endpoint}")

# Try a simple HTTP request to the server to see if the key is accepted
try:
    # We try to hit the health check or a basic endpoint
    url = endpoint.rstrip('/')
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, timeout=5)
    print(f"Server Response Code: {response.status_code}")
    if response.status_code == 200:
        print("🎉 SUCCESS: The server accepted the key!")
    else:
        print(f"❌ FAILED: The server rejected the key with code {response.status_code}")
except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
