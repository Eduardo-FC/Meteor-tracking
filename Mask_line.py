import cv2
import numpy as np

# Define line parameters
start_point = (100, 100)
end_point = (400, 400)
line_width = 5

# Load the video
cap = cv2.VideoCapture('v1.avi')

# Read the first frame
_, frame = cap.read()

# Create a black image with the same size as the frame
mask = np.zeros_like(frame)

# Define the line color
color = (255, 255, 255)

# Draw the line on the mask
cv2.line(mask, start_point, end_point, color, line_width)

# Apply the mask to the frame
framem = cv2.bitwise_and(frame, mask)

# Display the masked frame
cv2.imshow("Masked Frame", framem)
cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Loop through all frames in the video
while cap.isOpened():
    _, frame = cap.read()
    if frame is None:
        break

    # Apply the mask to the current frame
    frame = cv2.bitwise_and(frame, mask)

    # Display the masked frame
    cv2.imshow("Masked Frame", frame)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

# Release the video and destroy all windows
cap.release()
cv2.destroyAllWindows()
