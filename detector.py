import cv2
import numpy as np

from gemini_helper import get_gemini_analysis 
from labels import generate_cloud_label 

from gemini_helper import get_gemini_analysis # Changed to the new function
from labels import generate_cloud_label # Still used for comparison


def calculate_rarity_score(solidity, aspect_ratio):
    #Calculates a rarity score based on cloud properties.
    solidity_score = (1.0 - solidity) * 50
    aspect_ratio_score = abs(aspect_ratio - 1) * 10
    return int(solidity_score + aspect_ratio_score)

def detect_clouds(frame, total_seen):
    #detects the clouds in the img
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
        
        aspect_ratio = w / h if h != 0 else 0
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area != 0 else 0
        
        score = calculate_rarity_score(solidity, aspect_ratio)
        


        #Crop the cloud and send the image to Gemini

        cropped_cloud_img = frame[y:y+h, x:x+w]
        
        refined_label = get_gemini_analysis(cropped_cloud_img)



        # append the actual 'contour' and 'score' data

        cloud_info.append((x, y, w, h, refined_label, score, contour))
        
        leaderboard_data.append({
            "label": refined_label,
            "aspect_ratio": aspect_ratio,
            "solidity": solidity,
            "area": area,
            "score": score
        })

    total_seen += len(cloud_info)
    return total_seen, cloud_info, leaderboard_data
