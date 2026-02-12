
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def find_model():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    for m in genai.list_models():
        if "2.5" in m.name:
            print(f"Found: {m.name}")

if __name__ == "__main__":
    find_model()
