import cv2
import numpy as np
# --- CHANGE ---
# We are switching back to the Gemini helper.
from gemini_helper import refine_cloud_label
from labels import generate_cloud_label


def detect_clouds(frame, total_seen):
    # Convert the frame to grayscale for easier processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Threshold the image to isolate the bright clouds
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Find the outlines (contours) of the white areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cloud_info = []
    leaderboard_data = []

    for contour in contours:
        # Calculate the area of the contour to ignore small noise
        area = cv2.contourArea(contour)
        if area < 500:
            continue

        # Get the bounding box for placing text
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate various properties of the cloud's shape
        aspect_ratio = w / h
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area != 0 else 0

        # Generate the initial and refined labels for the cloud
        raw_label = generate_cloud_label(contour)
        refined_label = refine_cloud_label(raw_label)

        # Assign a mood emoji based on the cloud's properties
        mood = "😐"
        if aspect_ratio > 2.0:
            mood = "🤨"
        elif solidity < 0.5:
            mood = "💥"
        elif area > 5000:
            mood = "🍔"

        # We append the actual 'contour' data along with the other info
        cloud_info.append((x, y, w, h, refined_label, mood, contour))
        
        leaderboard_data.append({
            "label": refined_label,
            "aspect_ratio": aspect_ratio,
            "solidity": solidity,
            "area": area
        })

    total_seen += len(cloud_info)
    return total_seen, cloud_info, leaderboard_data
