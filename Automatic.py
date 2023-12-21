import cv2
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from tracker import EuclideanDistTracker
import os

# Get the name of the video file
video_file = 'video.avi'
video_name = os.path.splitext(video_file)[0]

# Create xlsx file name based on video title
xlsx_file = f"{video_name}_object_data.xlsx"

# Open the video file
cap = cv2.VideoCapture(video_file)

# Initialize variables
frame_index = 0

# Initialize tracker
tracker = EuclideanDistTracker()

# Initialize dataframe to store detections
df = pd.DataFrame(columns=['id', 'cx', 'cy', 'frame'])

# Get the first frame in grayscale
ret, previous_frame = cap.read()
previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

# Loop through the frames
while True:
    # Get the next frame in grayscale
    ret, current_frame = cap.read()
    if not ret:
        break
    current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

    # Subtract the previous frame from the current frame
    difference = cv2.absdiff(current_gray, previous_gray)
    cv2.imshow('difference', difference)


    # Apply the Canny edge detector
    edges = cv2.Canny(difference, 100, 200)

    # Dilate the edges
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)

    # Create a black rectangle at the bottom of the frame to remove noise
    height = 30
    cv2.rectangle(dilated, (0, current_frame.shape[0] - height), (current_gray.shape[1], current_frame.shape[0]), (0, 0, 0), -1)

    # Find contours in the dilated image
    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize list to store detections
    detections = []

    # Loop through all contours
    for cnt in contours:
        # Calculate contour area
        area = cv2.contourArea(cnt)

        # If contour area is large enough
        if area > 10:
            # Calculate moments of the contour
            M = cv2.moments(cnt)

            # If moment value is not zero
            if M["m00"] != 0:
                # Calculate centroid coordinates
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Draw centroid on the frame
                image = cv2.circle(current_frame, (cx, cy), radius=3, color=(0, 0, 255), thickness=-1)
                detections.append([cx, cy])

    # Update tracker with the detections
    boxes_ids = tracker.update(detections)

    # Loop through detected object boxes
    for box_id in boxes_ids:
        # Get object data
        cx, cy, id = box_id

        # Draw object id on the frame
        cv2.putText(image, str(id), (cx, cy - 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        # Add object data to the dataframe
        data = [id, cx, cy, frame_index]
        df.loc[len(df.index)] = data
        # Show the frame with detections
        cv2.imshow("Detection", image)

    # Update frame index
    frame_index += 1

    # Set the current frame and gray frame as the previous frame and gray frame for the next iteration
    previous_gray = current_gray

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

# Sort dataframe by object id and frame index
df_sorted = df.sort_values(by=['id', 'frame'])

# Save sorted dataframe to Excel file
df_sorted.to_excel(xlsx_file, sheet_name='Sheet1', index=False)

# Create root element for XML file
root = ET.Element('Detection')

# Iterate through sorted dataframe rows to create XML elements
for _, row in df_sorted.iterrows():
    # Create element for each object in each frame
    element = ET.SubElement(root, 'object')

    # Set element attributes
    element.set('id', str(row['id']))
    element.set('frame', str(row['frame']))
    element.set('cx', str(row['cx']))
    element.set('cy', str(row['cy']))

    # Add new line character at the end of each frame element
    element.tail = '\n'

# Write XML file
tree = ET.ElementTree(root)
xml_file = f"{video_name}_object_data.xml"
tree.write(xml_file, encoding='utf-8', xml_declaration=True)

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()