import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
import os
import time

# This path modification
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from detector import detect_clouds
from database import (
    add_user, check_user, get_user_profile, update_user_profile,
    add_xp, get_xp_for_next_level
)

# --- Page Configuration ---
st.set_page_config(page_title="CloudBooth ☁️", layout="wide")

# --- Custom UI/UX ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ADD8E6;
            color: black;
        }
        [data-testid="stSidebar"] * {
            color: black !important;
        }
        body {
            background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb');
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }
        .main {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 1rem;
            border-radius: 10px;
        }
        [data-testid="stSidebar"] hr {
            border: 1px solid black !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Main Application Logic ---

def main_app():
    """The main cloud analysis application, shown after login."""
    st.sidebar.title(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.divider()

    # Placeholders for dynamic sidebar content
    progress_placeholder = st.sidebar.empty()
    report_placeholder = st.sidebar.empty()

    def display_progress():
        """Renders the user's level and XP progress."""
        profile = st.session_state.user_profile
        with progress_placeholder.container():
            st.header("Your Progress")
            xp_needed = get_xp_for_next_level(profile['level'])
            st.write(f"**Level: {profile['level']}**")

            progress_bar = st.progress(0)
            progress_value = min(1.0, profile['xp'] / xp_needed if xp_needed > 0 else 1.0)
            progress_bar.progress(progress_value)

            st.write(f"{profile['xp']} / {xp_needed} XP")

            if st.session_state.get('leveled_up_message'):
                st.success(st.session_state.leveled_up_message)
                st.balloons()
                st.session_state.leveled_up_message = ""

    st.title("☁️ CloudBooth: The Sky’s Facial Recognition")
    st.markdown("Upload a picture of the sky, and we'll identify the clouds and give them clever names.")

    display_progress()

    uploaded_file = st.file_uploader("Upload a picture of the sky...", type=["jpg", "jpeg", "png"])

    if uploaded_file is None:
        report_placeholder.info("Upload an image to see your cloud report.")
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
                _, cloud_info, leaderboard_data = detect_clouds(frame_bgr, 0)

            display_image = frame_bgr.copy()
            # This loop now correctly unpacks 8 values, including the 'is_cloud' boolean
            for x, y, w, h, label, score, contour, is_cloud in cloud_info:
                if is_cloud:
                    # It's a cloud: draw in dark blue and show score
                    outline_color = (139, 0, 0)
                    text_content = f"{label} ({score} pts)"
                else:
                    # Not a cloud: draw in red and show simple label
                    outline_color = (0, 0, 255) # Red
                    text_content = "Not a cloud"

                cv2.drawContours(display_image, [contour], -1, outline_color, 3)
                cv2.putText(display_image, text_content, (x, y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 5)
                cv2.putText(display_image, text_content, (x, y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            with col2:
                st.header("Analyzed Image")
                st.image(cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB), use_container_width=True)

            st.success("Analysis Complete!")

            with report_placeholder.container():
                st.header("☁️ Cloud Report")
                if not leaderboard_data and not any(not c[7] for c in cloud_info):
                     st.info("No clouds were detected in this image.")
                else:
                    total_score = sum(cloud['score'] for cloud in leaderboard_data)

                    if total_score > 0:
                        leveled_up = add_xp(st.session_state.user_profile, total_score)
                        if leveled_up:
                            st.session_state.leveled_up_message = f"LEVEL UP! You are now Level {st.session_state.user_profile['level']}!"
                        update_user_profile(st.session_state.username, st.session_state.user_profile['level'], st.session_state.user_profile['xp'])

                    st.subheader("🏆 Leaderboard (Clouds Only)")
                    if leaderboard_data:
                        highest_scoring_cloud = max(leaderboard_data, key=lambda x: x['score'])
                        st.markdown(f"**Highest Score:** {highest_scoring_cloud['label']} ({highest_scoring_cloud['score']} pts)")
                        st.markdown(f"**Total XP Gained:** {total_score} pts")
                    else:
                        st.markdown("No valid clouds were scored in this image.")
                    st.divider()

                    st.subheader("📋 All Identified Clouds")
                    cloud_list = [c for c in leaderboard_data]
                    if cloud_list:
                        for cloud in sorted(cloud_list, key=lambda x: x['score'], reverse=True):
                            st.markdown(f"- {cloud['label']} ({cloud['score']} pts)")
                    else:
                        st.markdown("No valid clouds found.")
                    st.divider()

                    st.subheader("🧐 Other Objects Found")
                    non_clouds = [c for c in cloud_info if not c[7]]
                    if non_clouds:
                        for item in non_clouds:
                           st.markdown(f"- {item[4]}")
                    else:
                        st.markdown("No other objects were identified.")

            display_progress()

        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")

# --- Authentication Logic ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    st.title("☁️ Welcome to CloudBooth")

    choice = st.selectbox("Login or Signup", ["Login", "Signup"])

    if choice == "Login":
        with st.form("Login Form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if check_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_profile = get_user_profile(username)
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    elif choice == "Signup":
        with st.form("Signup Form"):
            username = st.text_input("Choose a Username")
            password = st.text_input("Choose a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Signup")

            if submitted:
                if password == confirm_password:
                    if add_user(username, password):
                        st.success("Account created successfully! Please login.")
                        st.balloons()
                    else:
                        st.error("Username already exists.")
                else:
                    st.error("Passwords do not match.")
