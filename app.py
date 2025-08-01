import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from detector import detect_clouds
# --- CHANGE: Import all character comment functions ---
from gemini_helper import get_tanjiro_comment, get_zenitsu_comment, get_inosuke_comment

# --- Custom CSS for the theme ---
def vibrant_style():
    css = """
    <style>
    /* Main app background */
    [data-testid="stAppViewContainer"] > .main {
        background-color: #FFF8DC; /* Light Gold (Cornsilk) background */
    }
    /* Sidebar background */
    [data-testid="stSidebar"] > div:first-child {
        background-color: #F5DEB3; /* Wheat color for sidebar */
    }
    /* Title and headers color */
    h1, h2, h3 {
        color: #000000; /* Black for high contrast */
    }
    /* Custom font for the title */
    h1 {
        font-family: 'Georgia', serif; /* A more classic, sharp font */
    }
    /* Text color */
    .st-emotion-cache-16txtl3, .st-emotion-cache-1629p8f, .st-emotion-cache-1ghh1go {
        color: #36454F; /* Dark Grey (Charcoal) for readability */
    }
    /* Button style */
    .stButton > button {
        color: #FFFFFF; /* Pure white text */
        background-color: #DAA520; /* Goldenrod button color */
        border-radius: 8px;
        border: 2px solid #DAA520;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #FFFFFF;
        color: #DAA520;
        border: 2px solid #DAA520;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --- Page Configuration ---
st.set_page_config(page_title="CloudBooth ☁️", layout="wide")
vibrant_style() 

# --- NEW: Character Selection ---
st.sidebar.title("Choose Your Guide")
character_choice = st.sidebar.selectbox(
    "Who do you want to analyze the clouds with?",
    ("Tanjiro", "Zenitsu", "Inosuke")
)

# Dictionary to hold character data
character_data = {
    "Tanjiro": {"image": "tanjiro.jpeg", "caption": "Tanjiro Kamado"},
    "Zenitsu": {"image": "zenitsu.jpeg", "caption": "Zenitsu Agatsuma"},
    "Inosuke": {"image": "inosuke.jpeg", "caption": "Inosuke Hashibira"}
}

selected_char_info = character_data[character_choice]
st.sidebar.image(selected_char_info["image"], caption=selected_char_info["caption"])
st.sidebar.divider()


st.title("☁️ CloudBooth: The Sky’s Image Analyzer")
st.markdown(f"Upload a picture of the sky, and **{character_choice}** will help you analyze the clouds!")

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a sky picture...", type=["jpg", "jpeg", "png"])

# --- Main App Logic ---
if uploaded_file is None:
    st.info("Please upload an image file to begin analysis.")
else:
    try:
        pil_image = Image.open(uploaded_file)
        frame = np.array(pil_image.convert('RGB'))
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        col1, col2 = st.columns(2)
        with col1:
            st.header("Original Image")
            st.image(pil_image, use_container_width=True)

        with st.spinner('Analyzing clouds... This may take a moment.'):
            total_clouds_seen, cloud_info, leaderboard_data = detect_clouds(frame_bgr, 0)

        display_image = frame_bgr.copy()

        for x, y, w, h, label, score, contour in cloud_info:
            cv2.drawContours(display_image, [contour], -1, (139, 0, 0), 3)
            cv2.putText(display_image, f"{label} ({score} pts)", (x, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 5) 
            cv2.putText(display_image, f"{label} ({score} pts)", (x, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        with col2:
            st.header("Analyzed Image")
            st.image(cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB), use_container_width=True)
        
        st.balloons()
        st.success("Analysis Complete!")

        # --- NEW: Dynamic Dialogue Box ---
        if leaderboard_data:
            total_score = sum(cloud['score'] for cloud in leaderboard_data)
            comment = ""
            if character_choice == "Tanjiro":
                comment = get_tanjiro_comment(total_score)
            elif character_choice == "Zenitsu":
                comment = get_zenitsu_comment(total_score)
            elif character_choice == "Inosuke":
                comment = get_inosuke_comment(total_score)

            with st.chat_message("assistant", avatar=selected_char_info["image"]):
                st.markdown(f"**{character_choice}:** {comment}")
        
        # --- Sidebar for Cloud Statistics ---
        st.sidebar.header("☁️ Cloud Report")
        if not leaderboard_data:
            st.sidebar.info("No clouds were detected in this image.")
        else:
            highest_scoring_cloud = max(leaderboard_data, key=lambda x: x['score'])
            total_score = sum(cloud['score'] for cloud in leaderboard_data)

            st.sidebar.subheader("🏆 Leaderboard")
            st.sidebar.markdown(f"**Highest Score:** {highest_scoring_cloud['label']} ({highest_scoring_cloud['score']} pts)")
            st.sidebar.markdown(f"**Total Score for Image:** {total_score} pts")
            st.sidebar.divider()
            
            st.sidebar.subheader("📋 All Identified Clouds")
            for cloud in sorted(leaderboard_data, key=lambda x: x['score'], reverse=True):
                st.sidebar.markdown(f"- {cloud['label']} ({cloud['score']} pts)")
            st.sidebar.divider()

            st.sidebar.subheader("🔢 Total Clouds Found")
            st.sidebar.markdown(f"**{len(leaderboard_data)}** clouds were identified.")

    except Exception as e:
        st.error(f"An error occurred while processing the image: {e}")
