import cv2
import pandas as pd
import numpy as np

# Read the xlsx files
df = pd.read_excel("v1_object_data.xlsx")
cx = df["cx"]
cy = df["cy"]
mx = df["mx"]
my = df["my"]

# Read the video
cap = cv2.VideoCapture("v1.avi")

# Create a window to display the result
cv2.namedWindow("line", cv2.WINDOW_NORMAL)
cv2.setWindowProperty('line', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

# Main loop
while True:
    # Capture a frame from the video source
    ret, frame = cap.read()

    # If the frame cannot be read, break the loop
    if not ret:
        break
    # Approximate the best lines
    rows, cols = frame.shape[:2]
    [vx, vy, x, y] = cv2.fitLine(np.array([cx, cy]).T, cv2.DIST_L2, 0, 0.01, 0.01)
    lefty = int((-x * vy / vx) + y)
    righty = int(((cols - x) * vy / vx) + y)
    cv2.line(frame, (cols - 1, righty), (0, lefty), (255, 0, 0), 1)
    # Plot the points and approximate the best lines
    for i in range(len(cx)):
        cv2.circle(frame, (cx[i], cy[i]), 0, (0, 0, 255), -1)

    for i in range(len(mx)):
        cv2.circle(frame, (mx[i], my[i]), 0, (0, 255, 0), -1)



    # Display the processed frame
    cv2.imshow("line", frame)

    # Check for key presses
    key = cv2.waitKey(0)
    if key == ord("q"):
        break

# Release the video source and close all windows
cap.release()
cv2.destroyAllWindows()
