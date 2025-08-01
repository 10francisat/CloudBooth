import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
import os

# This path modification 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from detector import detect_clouds

from gemini_helper import get_tanjiro_comment, get_zenitsu_comment, get_inosuke_comment

# --- Page Configuration ---
st.set_page_config(page_title="CloudBooth ☁️", layout="wide")

# --- Custom UI/UX: Sidebar color, Background Image, and Text Colors ---
st.markdown("""
    <style>
        /* Set sidebar background and text color */
        [data-testid="stSidebar"] {
            background-color: #ADD8E6;
            color: black;
        }

        [data-testid="stSidebar"] * {
            color: black !important;
        }

        /* Set full-page background image */
        body {
            background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb');
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }

        /* Optional: Make main content slightly opaque for readability */
        .main {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 1rem;
            border-radius: 10px;
            
        [data-testid="stSidebar"] hr {
    border: 1px solid black !important;
}
        }
    </style>
""", unsafe_allow_html=True)


# --- Page Configuration ---
st.set_page_config(page_title="CloudBooth ☁️", layout="wide")


# --- Welcome section in the sidebar ---
st.sidebar.title("Welcome, Cloud Slayer!")
# --- CHANGE: Using a local image file ---
# Make sure you have an image named 'sanemi.jpeg' in the same folder as this script.

st.sidebar.divider()


st.title("☁️ CloudBooth: The Sky’s Facial Recognition ")
st.markdown("Upload a picture of the sky, and we'll identify the clouds and give them clever names.")

# Upload File
uploaded_file = st.file_uploader("Upload the picture of the sky...", type=["jpg", "jpeg", "png"])


if uploaded_file is None:
    st.info("Please upload an image file to begin analysis.")
else:
    try:
        pil_image = Image.open(uploaded_file)
        frame = np.array(pil_image.convert('RGB'))
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        col1, col2 = st.columns(2)
        # Given Img Header
        with col1:
            st.header("Original Image")
            st.image(pil_image, use_container_width=True)

        with st.spinner('Analyzing clouds... This may take a moment.'):
            total_clouds_seen, cloud_info, leaderboard_data = detect_clouds(frame_bgr, 0)

        display_image = frame_bgr.copy()

        for x, y, w, h, label, score, contour in cloud_info:
            # High-contrast drawing colors
            # Outline color: Dark Blue
            cv2.drawContours(display_image, [contour], -1, (139, 0, 0), 3)
            # Text color: Pure White with a black outline for visibility
            cv2.putText(display_image, f"{label} ({score} pts)", (x, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 5) # Black outline
            cv2.putText(display_image, f"{label} ({score} pts)", (x, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2) # White text

        with col2:
            st.header("Analyzed Image")
            st.image(cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB), use_container_width=True)
        
        st.balloons()
        st.success("Analysis Complete!")

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