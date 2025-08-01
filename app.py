import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
from detector import detect_clouds
from gemini_utils import generate_cloud_label
from utils import convert_cv2_to_pil, encode_image_to_base64

st.set_page_config(page_title="AI Cloud Labeler ☁️", page_icon="🌥️", layout="centered")

st.title("☁️ AI Cloud Labeler with Gemini")
st.markdown("Upload a sky image or take a live capture to label cloud shapes creatively using Gemini 1.5 Flash!")

uploaded_image = st.file_uploader("Upload a sky image", type=["jpg", "jpeg", "png"])
capture_button = st.button("Take Live Webcam Capture")

image = None

# 1. Upload or capture an image
if uploaded_image:
    image = np.array(Image.open(uploaded_image).convert("RGB"))
elif capture_button:
    st.info("Initializing webcam...")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.success("Captured!")
    else:
        st.error("Failed to capture image.")

if image is not None:
    st.image(image, caption="Original Image", use_column_width=True)

    # 2. Detect clouds in the image
    st.subheader("⛅ Detected Clouds")
    cropped_clouds, bboxes, _ = detect_clouds(image)

    if not cropped_clouds:
        st.warning("No cloud-like shapes detected.")
    else:
        for idx, crop in enumerate(cropped_clouds):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(crop, caption=f"Cloud #{idx+1}", use_column_width=True)

            with col2:
                with st.spinner("Labeling..."):
                    label = generate_cloud_label(crop)
                st.success(f"Label: {label}")
