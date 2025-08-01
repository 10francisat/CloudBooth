import cv2
from labels import generate_cloud_label, random_emotion

def detect_clouds(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (15,15), 0)
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    count = 0
    cloud_data = []
    leaderboard_data = []

    for c in contours:
        area = cv2.contourArea(c)
        if area > 3000:
            count += 1
            x, y, w, h = cv2.boundingRect(c)
            label = generate_cloud_label(c)
            mood = random_emotion()
            cloud_data.append((x, y, w, h, label, mood))

            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            aspect_ratio = w / h if h != 0 else 0
            solidity = area / hull_area if hull_area != 0 else 1
            leaderboard_data.append({
                "label": label,
                "area": area,
                "aspect_ratio": aspect_ratio,
                "solidity": solidity
            })

    return count, cloud_data, leaderboard_data
