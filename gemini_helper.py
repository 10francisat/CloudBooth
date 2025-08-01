import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import cv2

# Load environment variables from a .env file
load_dotenv()

# --- Gemini API Configuration ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None
    st.warning("GOOGLE_API_KEY not found. Please set it in your .env file or Streamlit secrets.")

def get_gemini_analysis(cloud_image_np):
    """
    Uses the Gemini Vision model to analyze an image of a cloud.
    """
    if model is None:
        return "[Gemini API key not configured]"

    # Convert the OpenCV image (NumPy array) to a PIL Image for Gemini
    pil_image = Image.fromarray(cv2.cvtColor(cloud_image_np, cv2.COLOR_BGR2RGB))

    # --- NEW, MORE POWERFUL PROMPT ---
    prompt = """
    You are a creative and imaginative cloud spotter, an expert in pareidolia.
    Look closely at the provided image of a single cloud.
    Describe what you *really* see in its shape. Does it look like an animal, an object, a face, or something else?
    Be descriptive and imaginative. Give it a creative name based on what you see.
    
    Respond with the name only. For example: "A Dragon Taking Flight", "A Sleeping Cat", "A Leaky Teapot".
    Just return the name. No quotes, no explanation.
    """

    try:
        # Send both the prompt and the image to the model
        response = model.generate_content([prompt, pil_image])
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "[Gemini error]"
