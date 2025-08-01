import streamlit as st
import cv2
import numpy as np
from PIL import Image

# We need to make sure the other helper files can be found
# This handles potential import issues depending on how the app is run
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detector import detect_clouds

# --- Page Configuration ---
st.set_page_config(page_title="CloudBooth ☁️", layout="wide")
st.title("☁️ CloudBooth: The Sky’s Image Analyzer")
st.markdown("Upload a picture of the sky, and we'll identify the clouds and give them clever names.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a sky picture...", type=["jpg", "jpeg", "png"])

# --- Main App Logic ---
if uploaded_file is None:
    st.info("Please upload an image file to begin analysis.")
else:
    # This block runs only after a file has been uploaded
    try:
        # Read the uploaded file into an image that OpenCV can use
        pil_image = Image.open(uploaded_file)
        frame = np.array(pil_image.convert('RGB'))
        # OpenCV uses BGR format, so we convert from RGB
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Use columns for a side-by-side layout
        col1, col2 = st.columns(2)

        with col1:
            st.header("Original Image")
            st.image(pil_image, use_container_width=True)

        # --- Cloud Detection and Drawing ---
        # Show a spinner while the analysis is running
        with st.spinner('Analyzing clouds... This may take a moment.'):
            # The 'total_clouds_seen' starts at 0 for each new image
            total_clouds_seen, cloud_info, leaderboard_data = detect_clouds(frame_bgr, 0)

        display_image = frame_bgr.copy()

        # Loop through the detected clouds and draw their outlines and labels
        for x, y, w, h, label, mood, contour in cloud_info:
            # Draw the precise outline of the cloud in green
            cv2.drawContours(display_image, [contour], -1, (0, 255, 0), 3)
            # Put the generated label and mood above the cloud
            cv2.putText(display_image, f"{label} ({mood})", (x, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        with col2:
            st.header("Analyzed Image")
            # Convert the color back to RGB for correct display in Streamlit
            st.image(cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB), use_container_width=True)
        
        # --- Add the emoji shower ---
        st.balloons()
        st.success("Analysis Complete!")

        # --- Sidebar for Cloud Statistics ---
        st.sidebar.header("☁️ Cloud Stats for this Image")
        if not leaderboard_data:
            st.sidebar.info("No clouds were detected in this image.")
        else:
            # Sort clouds by area to find the biggest
            biggest_cloud = max(leaderboard_data, key=lambda x: x['area'])
            # Sort clouds by aspect ratio to find the longest
            longest_cloud = max(leaderboard_data, key=lambda x: x['aspect_ratio'])
            # Sort clouds by solidity to find the most "explosive"
            explosive_cloud = min(leaderboard_data, key=lambda x: x['solidity'])

            st.sidebar.subheader("🏆 Biggest Cloud")
            st.sidebar.markdown(f"**{biggest_cloud['label']}** — Area: {biggest_cloud['area']:.0f} pixels")
            
            st.sidebar.subheader("📏 Longest Cloud")
            st.sidebar.markdown(f"**{longest_cloud['label']}** — Aspect Ratio: {longest_cloud['aspect_ratio']:.2f}")

            st.sidebar.subheader("💥 Most Explosive")
            st.sidebar.markdown(f"**{explosive_cloud['label']}** — Solidity: {explosive_cloud['solidity']:.2f}")

            st.sidebar.subheader("🔢 Total Clouds Found")
            st.sidebar.markdown(f"**{len(leaderboard_data)}** clouds were identified.")

    except Exception as e:
        st.error(f"An error occurred while processing the image: {e}")
