import random
import cv2

def generate_cloud_label(contour):
    x, y, w, h = cv2.boundingRect(contour)
    area = cv2.contourArea(contour)
    rect_area = w * h

    aspect_ratio = w / h
    extent = area / rect_area if rect_area != 0 else 0
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area != 0 else 0
# AR
    if aspect_ratio > 2.5:
        return "Long cloud"
    elif aspect_ratio < 0.4:
        return "Tall cloud"
    elif 0.9 < aspect_ratio < 1.1:
        if solidity > 0.9:
            return "Round solid cloud"
        else:
            return "Round hollow cloud"
    elif extent < 0.3:
        return "Sparse cloud"
    elif solidity < 0.5:
        return "Explosive cloud"
    else:
        return random.choice(["Fluffy shape", "Blobby cloud", "Weird puff", "Indistinct mass"])

def random_emotion():
    emotions = ["happy", "sad", "angry", "sarcastic", "excited", "bored"]
    return random.choice(emotions)

