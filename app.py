import streamlit as st
import cv2
from detector import detect_clouds

st.set_page_config(page_title="CloudBooth ☁️", layout="wide")
st.title("☁️ CloudBooth: The Sky’s Facial Recognition System")

video_file = st.file_uploader("Upload a sky video (or leave blank for webcam)", type=["mp4"])

run_app = st.button("Start Judging Clouds")

longest_cloud = {"label": "", "aspect_ratio": 0}
explosive_cloud = {"label": "", "solidity": 1}
biggest_cloud = {"label": "", "area": 0}

if run_app:
    stframe = st.empty()
    cap = cv2.VideoCapture(0 if video_file is None else video_file.name)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cloud_count, cloud_info, leaderboard_data = detect_clouds(frame)

        for data in leaderboard_data:
            if data["aspect_ratio"] > longest_cloud["aspect_ratio"]:
                longest_cloud = {"label": data["label"], "aspect_ratio": data["aspect_ratio"]}
            if data["solidity"] < explosive_cloud["solidity"]:
                explosive_cloud = {"label": data["label"], "solidity": data["solidity"]}
            if data["area"] > biggest_cloud["area"]:
                biggest_cloud = {"label": data["label"], "area": data["area"]}

        display = frame.copy()
        for x, y, w, h, label, mood in cloud_info:
            cv2.rectangle(display, (x, y), (x+w, y+h), (255,255,255), 2)
            cv2.putText(display, f"{label} ({mood})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        cv2.putText(display, f"Clouds: {cloud_count}", (20,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        stframe.image(display, channels="BGR")

    cap.release()

# Sidebar Leaderboard
with st.sidebar:
    st.header("🏆 Cloud Leaderboard")
    st.subheader("☁️ Longest Cloud")
    st.markdown(f"**{longest_cloud['label']}** — AR: {longest_cloud['aspect_ratio']:.2f}")
    st.subheader("💥 Most Explosive")
    st.markdown(f"**{explosive_cloud['label']}** — Solidity: {explosive_cloud['solidity']:.2f}")
    st.subheader("🍔 Biggest Cloud")
    st.markdown(f"**{biggest_cloud['label']}** — Area: {biggest_cloud['area']:.0f}")
