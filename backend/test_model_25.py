
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_25():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content("ping")
        print(f"Success! Model 'gemini-2.5-pro' responded.")
    except Exception as e:
        print(f"Error for 'gemini-2.5-pro': {e}")
        
    try:
        model = genai.GenerativeModel("gemini-2.5-pro-preview")
        response = model.generate_content("ping")
        print(f"Success! Model 'gemini-2.5-pro-preview' responded.")
    except Exception as e:
        print(f"Error for 'gemini-2.5-pro-preview': {e}")

if __name__ == "__main__":
    test_25()
