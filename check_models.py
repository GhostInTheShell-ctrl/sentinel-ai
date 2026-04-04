import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("--- Available Models for your API Key ---")
try:
    for model in client.models.list():
        print(f"Name: {model.name} | Version: {model.version}")
except Exception as e:
    print(f"Error fetching models: {e}")