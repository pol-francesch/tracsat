import numpy as np 
# from cv2 import cv2
import cv2

# Getting video
cap = cv2.VideoCapture(0)


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    print('Got frame')

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print('Converted to grayscale')
