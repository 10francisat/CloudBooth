import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv

# --- CHANGE: Load environment variables from a .env file ---
# This line looks for a .env file in your project directory and loads it.
load_dotenv() 

# --- Gemini API Configuration ---
# This part of the code now works perfectly with your .env file.
# os.getenv will find the key that load_dotenv() made available.
try:
    # Try to get the key from Streamlit's secrets management first (for deployment)
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    # If not deployed, fall back to the environment variables loaded from your .env file
    api_key = os.getenv("GOOGLE_API_KEY")

# Configure the genai library with the API key
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    # If no key is found, set the model to None to prevent crashes
    model = None
    st.warning("GOOGLE_API_KEY not found. Please set it in your .env file or Streamlit secrets.")


def refine_cloud_label(description):
    """
    Uses the Gemini API to generate a creative name for a cloud.
    """
    # If the model couldn't be loaded, return a fallback message.
    if model is None:
        return "[Gemini API key not configured]"

    # The prompt to give the AI its personality and task.
    prompt = f"""
    You are a sarcastic cloud-naming expert. A user described a cloud as "{description}".
    Come up with a short, clever name that sounds like it came from a weather-themed comic book.
    Just return the name only, no quotes, no explanation.
    """

    try:
        # Call the Gemini API to generate content
        response = model.generate_content(prompt)
        # Return the cleaned-up text from the response
        return response.text.strip()
    except Exception as e:
        # If an error occurs during the API call, return an error message.
        print(f"Gemini API error: {e}")
        return f"[Gemini error]"
