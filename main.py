import requests
import json
import os
from dotenv import load_dotenv

# ─── Load environment variables from .env file ────────────────────────────────
load_dotenv(override=True)  # override=True allows .env values to overwrite existing env vars

# ─── Configuration ────────────────────────────────────────────────────────────
API_KEY = os.getenv("ANTHROPIC_API_KEY")
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
ENDPOINT = f"{BASE_URL}/v1/messages"

# ─── Headers (same as Postman Headers tab) ────────────────────────────────────
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# ─── Request Body (same as Postman Body → raw → JSON) ─────────────────────────
payload = {
    "model": os.getenv("MODEL_NAME"),
    "max_tokens": 256,
    "temperature": 0.5,
    "system": "You are a helpful assistant.",
    "messages": [
        {
            "role": "user",
            "content": "What is the capital of Canada?"
        }
    ]
}

# ─── Send POST Request ─────────────────────────────────────────────────────────
response = requests.post(ENDPOINT, headers=headers, json=payload)

# ─── Display Response ──────────────────────────────────────────────────────────
print(f"Status Code : {response.status_code}")
print(f"Response    :\n{json.dumps(response.json(), indent=2)}")

# ─── Extract just the assistant's reply ───────────────────────────────────────
if response.status_code == 200:
    reply = response.json()["content"][0]["text"]
    print(f"\nClaude says: {reply}")
