
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def test_rest_api():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        return
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    { "text": "Hello, explain briefly who you are." }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 100
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing gemini-3-flash via REST...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            if response.status_code == 200:
                print("Success!")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"Failed with status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_rest_api())
