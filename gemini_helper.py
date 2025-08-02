import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import cv2

# Load environment variables from a .env file
load_dotenv()

# Gemini API Configuration
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
    First, verifies if the image contains a cloud. If it does, it gives it a creative name.
    If not, it returns a special keyword.
    """
    if model is None:
        return "NO_CLOUD"

    pil_image = Image.fromarray(cv2.cvtColor(cloud_image_np, cv2.COLOR_BGR2RGB))

    # New prompt to first validate if the object is a cloud
    prompt = """
    Analyze the image.
    1. Is the main object in this image a cloud? Answer with "Yes" or "No".
    2. If the answer is "Yes", on a new line, provide a creative and imaginative name for the cloud's shape (e.g., "A Dragon Taking Flight").

    If it is not a cloud, just respond with "No".
    """
    try:
        response = model.generate_content([prompt, pil_image])
        text_response = response.text.strip()

        # Check if the model responded that it's not a cloud
        if text_response.lower().startswith("no"):
            return "NO_CLOUD"

        # If it is a cloud, extract the name from the second line
        lines = text_response.split('\n')
        if len(lines) > 1 and lines[0].lower().startswith("yes"):
            return lines[1].strip()
        # Fallback if the model doesn't follow the multi-line instruction perfectly
        elif not text_response.lower().startswith("yes"):
            return text_response
        else:
            return "Unusual Cloud Shape"

    except Exception as e:
        print(f"Gemini API error: {e}")
        return "[Gemini error]"

def get_tanjiro_comment(total_score):
    """
    Generates an encouraging comment in Tanjiro's character based on the score.
    """
    if model is None: return "..."
    if total_score > 100:
        template = "Wow, {score} points! That's an incredible score! Your hard work and focus are really paying off. I'm so impressed!"
    elif total_score > 50:
        template = "You got {score} points! That's a great result. I can tell you're doing your best. Let's keep this momentum going!"
    else:
        template = "{score} points is a good start! Don't be discouraged. Every attempt helps us learn. Take a deep breath, and let's try again together!"
    prompt = f"You are Tanjiro Kamado. Respond to a user's score with this template: '{template}'. Be kind and supportive."
    try:
        response = model.generate_content(prompt.format(score=total_score))
        return response.text.strip()
    except Exception: return "Oh no, something went wrong."

def get_zenitsu_comment(total_score):
    """
    Generates a comment in Zenitsu's character based on the score.
    """
    if model is None: return "..."
    if total_score > 100:
        template = "{score} POINTS?! I DID IT! I mean, WE did it! I knew I had it in me! This is amazing! I'm not useless after all!"
    elif total_score > 50:
        template = "{score} points? That's... not terrible? Are you sure? I was so scared the whole time! I thought we were gonna fail for sure!"
    else:
        template = "WAAAAH! Only {score} points?! It's over! We're doomed! I can't do this, it's too scary! I need to protect Nezuko-chan!"
    prompt = f"You are Zenitsu Agatsuma. Respond to a user's score with this template: '{template}'. Be very emotional and scared, but proud of high scores."
    try:
        response = model.generate_content(prompt.format(score=total_score))
        return response.text.strip()
    except Exception: return "I'm too scared to think!"

def get_inosuke_comment(total_score):
    """
    Generates a comment in Inosuke's character based on the score.
    """
    if model is None: return "..."
    if total_score > 100:
        template = "HAHAHA! {score} POINTS! I AM THE KING OF THE MOUNTAINS AND THE KING OF THE CLOUDS! BOW BEFORE MY MIGHTY POWER!"
    elif total_score > 50:
        template = "{score} points! A worthy offering for the great Inosuke! Now, bring me a stronger opponent! These clouds were too easy!"
    else:
        template = "ONLY {score}?! ARE YOU KIDDING ME?! THESE WEAKLING CLOUDS AREN'T WORTHY OF MY GAZE! FIGHT ME, SKY!"
    prompt = f"You are Inosuke Hashibira. Respond to a user's score with this template: '{template}'. Be loud, arrogant, and always ready for a fight."
    try:
        response = model.generate_content(prompt.format(score=total_score))
        return response.text.strip()
    except Exception: return "RAAAGH!"
