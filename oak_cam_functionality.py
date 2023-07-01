#!/usr/bin/env python
# coding: utf-8

# In[2]:


#Use OAK cam to caputre clear high res img when press spacebar
#then uses OCR on that clear img to detect text. 
import cv2
import depthai
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import uuid
import os
import time
import keyboard

# Create the pipeline
pipeline = depthai.Pipeline()
# Create the input (color camera) and output (video file) nodes
cam_rgb = pipeline.createColorCamera()
video_out = pipeline.createXLinkOut()

# Set camera properties
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(True)

# Define the video output stream
video_out.setStreamName("preview")

# Link the nodes
cam_rgb.preview.link(video_out.input)

# Connect to the device
with depthai.Device(pipeline) as device:
    # Start the pipeline
    device.startPipeline()

    # Create output queue for preview stream
    preview_queue = device.getOutputQueue("preview", 1, True)

    while True:
        # Get the preview frame
        preview_data = preview_queue.get()

        # Retrieve the OpenCV BGR frame
        frame_bgr = preview_data.getCvFrame()

        # Display the frame
        cv2.imshow("Oak-D Camera", frame_bgr)

        # Capture an image when 'Space' key is pressed
        #if cv2.waitKey(1) == ord(" "):
        if keyboard.is_pressed("space"):
            # Save the frame as an image
            cv2.imwrite("captured_image.jpg", frame_bgr)
            print("Image captured!")
            img = cv2.imread('captured_image.jpg')
            reader = easyocr.Reader(['en'])
            result = reader.readtext(img)
            #print(result[0])
            print(result)
            break

        # Exit the loop when 'Esc' key is pressed
        if cv2.waitKey(1) == 27:
            break

    # Release resources
    cv2.destroyAllWindows()


# In[2]:


import cv2
import depthai
import easyocr
import keyboard

# Create the pipeline
pipeline = depthai.Pipeline()
# Create the input (color camera) and output (video file) nodes
cam_rgb = pipeline.createColorCamera()
video_out = pipeline.createXLinkOut()

# Set camera properties
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(True)

# Define the video output stream
video_out.setStreamName("preview")

# Link the nodes
cam_rgb.preview.link(video_out.input)

# Connect to the device
device = depthai.Device()
device.startPipeline(pipeline)

# Create output queue for preview stream
preview_queue = device.getOutputQueue("preview", 1, True)

while True:
    # Get the preview frame
    preview_data = preview_queue.get()

    # Retrieve the OpenCV BGR frame
    frame_bgr = preview_data.getCvFrame()

    # Display the frame
    cv2.imshow("Oak-D Camera", frame_bgr)

    # Capture an image when 'Space' key is pressed
    i=0
    
    if keyboard.is_pressed("space"):
        # Save the frame as an image
        cv2.imwrite("captured_image.jpg", frame_bgr)
        print("Image captured!")
        img = cv2.imread('captured_image.jpg')
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img)
        print(result)
        break

    # Exit the loop when 'Esc' key is pressed
    if cv2.waitKey(1) == 27:
        break

# Release resources
cv2.destroyAllWindows()


# In[4]:


img = cv2.imread('captured_image.jpg')
reader = easyocr.Reader(['en'])
result = reader.readtext(img)
print(result)


# In[1]:


import cv2
import depthai
import easyocr
import keyboard

# Create the pipeline
pipeline = depthai.Pipeline()
# Create the input (color camera) and output (video file) nodes
cam_rgb = pipeline.createColorCamera()
video_out = pipeline.createXLinkOut()

# Set camera properties
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(True)

# Define the video output stream
video_out.setStreamName("preview")

# Link the nodes
cam_rgb.preview.link(video_out.input)

# Connect to the device
device = depthai.Device()
device.startPipeline(pipeline)

# Create output queue for preview stream
preview_queue = device.getOutputQueue("preview", 1, True)

for _ in range(10):
    while True:
        # Get the preview frame
        preview_data = preview_queue.get()

        # Retrieve the OpenCV BGR frame
        frame_bgr = preview_data.getCvFrame()

        # Display the frame
        cv2.imshow("Oak-D Camera", frame_bgr)

        # Capture an image when 'Space' key is pressed
        if keyboard.is_pressed("space"):
            # Save the frame as an image
            cv2.imwrite("captured_image.jpg", frame_bgr)
            print("Image captured!")
            img = cv2.imread('captured_image.jpg')
            reader = easyocr.Reader(['en'])
            result = reader.readtext(img)
            print(result)
            break

        # Exit the loop when 'Esc' key is pressed
        if cv2.waitKey(1) == 27:
            break

# Release resources
cv2.destroyAllWindows()

