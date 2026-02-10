import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"DEBUG: Loaded API Key: {api_key[:5] if api_key else 'None'}...")
if not api_key:
    print("ERROR: GOOGLE_API_KEY is missing!")
else:
    gm_path = genai.__file__
    print(f"DEBUG: genai path: {gm_path}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content("Hello, are you working?")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
