#!/usr/bin/env python
# coding: utf-8

# In[5]:


get_ipython().system('pip install easyocr')
get_ipython().system('pip install imutils')
get_ipython().system('pip install opencv-python-headless')
get_ipython().system('pip install opencv-python')


# In[2]:


import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr


# In[3]:


# Import opencv
import cv2 

# Import uuid
import uuid

# Import Operating System
import os

# Import time
import time


# In[4]:


labels = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine','ten', 'eleven', 'twelve']
#number_imgs = 12


# In[5]:


IMAGES_PATH = os.path.join('images', 'collectedimages')


# In[6]:


if not os.path.exists(IMAGES_PATH):
    if os.name == 'posix':
        get_ipython().system('mkdir -p {IMAGES_PATH}')
    if os.name == 'nt':
         get_ipython().system('mkdir {IMAGES_PATH}')
for label in labels:
    path = os.path.join(IMAGES_PATH, label)
    if not os.path.exists(path):
        get_ipython().system('mkdir {path}')


# In[7]:


#init the reader object
reader = easyocr.Reader(['en'])


# In[8]:


#img = cv2.imread('streetHouse.png') #works
#img = cv2.imread('Modern-house-number-sign.png') #works
img = cv2.imread('captured_image_0.jpg')
#img = cv2.imread('WIN_20230524_12_22_27_Pro.jpg') #kinda worked: called a 1 an 'I'
# img = cv2.imread('WIN_20230524_12_25_38_Pro.jpg')#worked
#img = cv2.imread('WIN_20230524_12_27_31_Pro.jpg') #kinda worked called a 4 a '4L'
#img = cv2.imread('WIN_20230524_12_39_15_Pro.jpg') # worked
plt.imshow(img)
result = reader.readtext(img)
result


# In[9]:


#Code to loop through each label (jersey number) and take 5 pic for each
labels = ['six']
for label in labels:
    cap = cv2.VideoCapture(1)
    print('Collecting images for {}'.format(label))
    time.sleep(5)
    for imgnum in range(2):      #the two indicates how many pics it will take per folder
        print('Collecting image {}'.format(imgnum))
        ret, frame = cap.read()
        imgname = os.path.join(IMAGES_PATH,label,label+'.'+'{}.jpg'.format(str(uuid.uuid1())))
        cv2.imwrite(imgname, frame)
        cv2.imshow('frame', frame)
        time.sleep(5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()


# In[19]:


# sav_file = 'one' # you can choose where to save the pic that its gonna take
# cap = cv2.VideoCapture(1)
# for imgnum in range(5):
#         print('Collecting image {}'.format(imgnum))
#         ret, frame = cap.read()
#         imgname = os.path.join(IMAGES_PATH,sav_file,sav_file+'.'+'{}.jpg'.format(str(uuid.uuid1())))
#         cv2.imwrite(imgname, frame)
#         cv2.imshow('frame', frame)
#         time.sleep(5)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
            
# cap.release()
# cv2.destroyAllWindows()


# In[15]:


get_ipython().system('pip install --upgrade opencv-python')


# In[16]:


get_ipython().system('pip install pywin32')


# In[12]:


# import cv2
# import easyocr
# import matplotlib.pyplot as plt

# # Initialize the reader
# reader = easyocr.Reader(['en'])

# Image path
image_path = "WIN_20230524_12_39_15_Pro.jpg"

# Read the image
img = cv2.imread(image_path)

if img is not None:
    # Image loaded successfully, proceed with processing
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect text using OCR
    result = reader.readtext(gray)
    print(result)
    # Draw bounding boxes on the image
    for detection in result:
        bbox = detection[0]
        text = detection[1]
        confidence = detection[2]

        # Extract the coordinates of the bounding box
        x_min, y_min = bbox[0]
        x_max, y_max = bbox[2]

        # Draw the bounding box rectangle and text on the image
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(img, text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the image with bounding boxes
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()
else:
    print("Failed to load the image.")


# In[7]:


#openCv test cell that takes in an a passed image: works
import cv2

#image_path = "Modern-house-number-sign.png"
image_path = "WIN_20230524_12_39_15_Pro.jpg"
img = cv2.imread(image_path)

if img is not None:
    # Image loaded successfully, proceed with saving
    cv2.imwrite("output.jpg", img)
else:
    print("Failed to load the image.")

plt.imshow(img)
result = reader.readtext(img)
result


# In[18]:


#openCV test to open the camera && takes a pic when you press spacebar

# Open the default camera (usually the first camera available)
cap = cv2.VideoCapture(0)
i=0
# Check if the camera opened successfully
if not cap.isOpened():
    print("Failed to open the camera")
    exit()

# Continuously read frames from the camera
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If the frame was not captured successfully, break the loop
    if not ret:
        print("Failed to capture frame from the camera")
        break

    # Display the resulting frame
    cv2.imshow("Camera", frame)

    # Check if the space bar is pressed
    if cv2.waitKey(1) == ord(' '):
        # Save the frame as an image
        filename = f"captured_image_{i}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Image {filename} captured!")
        i+=1

    # Wait for the 'q' key to be pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()


# In[4]:


#openCV test to open the camera && takes a pic when you click
# import cv2
# import easyocr
# from PIL import Image

# Initialize the reader
reader = easyocr.Reader(['en'])

# Initialize the filename variable
filename = ""
# Counter for image filenames
i = 0

# Mouse event callback function
def mouse_callback(event, x, y, flags, param):
    global filename
    if event == cv2.EVENT_LBUTTONDOWN:
        # Save the frame as an image
        global i
        filename = f"captured_image_{i}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Image {filename} captured!")

        # Read the image using PIL and pass it to the reader
        img = cv2.imread(filename)
        #img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        result = reader.readtext(img)
        #jersey_number = result[0][1][0]
        #confidence = result[0][0][0]
        #print("Jersey #: ", jersey_number, "\nConfidence: ", confidence, "\n")
        print(result)

        i += 1

# Open the default camera (usually the first camera available)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Failed to open the camera")
    exit()

# Set the mouse callback function
cv2.namedWindow("Camera")
cv2.setMouseCallback("Camera", mouse_callback)

# Continuously read frames from the camera
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If the frame was not captured successfully, break the loop
    if not ret:
        print("Failed to capture frame from the camera")
        break

    # Display the resulting frame
    cv2.imshow("Camera", frame)

    # Wait for the 'q' key to be pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()


# In[8]:


#Culmination of it all: where you open cam, take a pic, save it to the directory, and pass the pic to the reader to read
    # the number on the jersey and the console displays the jersey#
reader = easyocr.Reader(['en'])

#init filename so you can access it thru-out whole cell
filename = ""
imgList = []
# Open the default camera (usually the first camera available)
cap = cv2.VideoCapture(0)
i=0
# Check if the camera opened successfully
if not cap.isOpened():
    print("Failed to open the camera")
    exit()

# Continuously read frames from the camera
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If the frame was not captured successfully, break the loop
    if not ret:
        print("Failed to capture frame from the camera")
        break

    # Display the resulting frame
    cv2.imshow("Camera", frame)

    # Check if the space bar is pressed
    if cv2.waitKey(1) == ord(' '):
        # Save the frame as an image
        filename = f"captured_image_{i}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Image {filename} captured!")
        #img = filename
        img = cv2.imread(filename)
        imgList.append(img)
        #plt.imshow(img)
        result = reader.readtext(img)
        jersey_number = result[0][1][0]
        print("Jersey #: ", jersey_number)
        #print(result) this would print the entire tuple of result information in the format of:
            #[[bounding boxes], [detected_text], [confidence]]
        i+=1

    # Wait for the 'q' key to be pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()

for i in imgList:
    plt.imshow(i)
# plt.imshow(img)
# result = reader.readtext(img)
# result


# In[7]:


#now I want to have a live video detect the jersey# and display it in the frame while
# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])

# Open the default camera (usually the first camera available)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Failed to open the camera")
    exit()

# Continuously read frames from the camera
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If the frame was not captured successfully, break the loop
    if not ret:
        print("Failed to capture frame from the camera")
        break

    # Display the resulting frame
    cv2.imshow("Camera", frame)

    # Convert the frame to grayscale for text detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform text detection
    result = reader.readtext(gray)
    
    #get dimensions of the frame
    frame_height, frame_width, _ = frame.shape
    center_x = int(frame_width / 2)
    center_y = int(frame_height / 2)
    
    # Process the result to extract the jersey number
    for detection in result:
        bbox = detection[0]
        text = detection[1]
        confidence = detection[2]
        print(f"Detected Text: {text}")
        #print(f"Bounding Box: {bbox}")
        #print(f"Confidence: {confidence}")
        # Display the detected text on the frame
        cv2.putText(frame, 'j', (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
        #cv2.putText(frame, text, (bbox[0][0], bbox[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        #cv2.rectangle(frame, tuple(bbox[0]), tuple(bbox[2]), (0, 255, 0), 2)

        print("----------------------")
        # Add your logic here to further process the detected text, e.g., extract the jersey number

    # Wait for the 'q' key to be pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()


# In[23]:


#the above works for what I need it to but I want to see if I can zoom
# in w/ the camera so this is just a test to simply open the camera
# and zoom in and out when I click 


# Open the video capture
cap = cv2.VideoCapture(0)

# Initialize the zoom flag
zoom_in = False

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # Get the frame dimensions
    height, width = frame.shape[:2]

    # Calculate the zoomed region of interest (ROI)
    zoom_factor = 1.5 if zoom_in else 1.0
    roi_width = int(width / zoom_factor)
    roi_height = int(height / zoom_factor)
    x = int((width - roi_width) / 2)
    y = int((height - roi_height) / 2)
    roi = frame[y:y+roi_height, x:x+roi_width]

    # Display the zoomed ROI
    cv2.imshow("Camera", roi)

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF

    # Toggle zoom in when spacebar is pressed
    if key == ord(' '):
        zoom_in = not zoom_in

    # Exit the loop if the 'q' key is pressed
    if key == ord('q'):
        break

# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()

