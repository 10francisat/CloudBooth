def generate_cloud_label(contour):
    import cv2
    import random

    x, y, w, h = cv2.boundingRect(contour)
    area = cv2.contourArea(contour)
    rect_area = w * h

    aspect_ratio = w / h
    extent = area / rect_area if rect_area != 0 else 0
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area != 0 else 0

    # Pattern-based logic
    if aspect_ratio > 2.5:
        return "Sky Noodle"
    elif aspect_ratio < 0.4:
        return "Leaning Tower Cloud"
    elif 0.9 < aspect_ratio < 1.1:
        if solidity > 0.9:
            return "Cloud Bonda"
        else:
            return "Almost Circle"
    elif extent < 0.3:
        return "Fluffy Impostor"
    elif solidity < 0.5:
        return "Angry Explosion Cloud"
    else:
        adjectives = ["Suspicious", "Uncertain", "Majestic", "Dramatic"]
        nouns = ["Samosa", "Potato", "Duck", "Blob"]
        return f"{random.choice(adjectives)} {random.choice(nouns)}"