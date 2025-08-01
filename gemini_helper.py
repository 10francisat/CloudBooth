import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini with your key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Create model instance
model = genai.GenerativeModel("models/gemini-1.5-flash")

def refine_cloud_label(description):
    prompt = f"""
    You are a sarcastic cloud-naming expert. A user described a cloud as "{description}".
    Come up with a short, clever name that sounds like it came from a weather-themed comic book.
    Just return the name only, no quotes, no explanation.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini error: {str(e)}]"
