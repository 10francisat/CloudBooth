import cv2
import numpy as np
from labels import generate_cloud_label
from gemini_helper import refine_cloud_label

def detect_clouds(frame, total_seen):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cloud_info = []
    leaderboard_data = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        rect_area = w * h
        extent = area / rect_area if rect_area != 0 else 0
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area != 0 else 0

        raw_label = generate_cloud_label(contour)
        refined_label = refine_cloud_label(raw_label)

        mood = "😐"
        if aspect_ratio > 2.0:
            mood = "🤨"
        elif solidity < 0.5:
            mood = "💥"
        elif area > 5000:
            mood = "🍔"

        cloud_info.append((x, y, w, h, refined_label, mood))
        leaderboard_data.append({
            "label": refined_label,
            "aspect_ratio": aspect_ratio,
            "solidity": solidity,
            "area": area
        })

    total_seen += len(cloud_info)
    return total_seen, cloud_info, leaderboard_data
