
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash")
    
    try:
        print("Testing gemini-3-flash...")
        response = model.generate_content("Hello")
        print("Success!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_model()
