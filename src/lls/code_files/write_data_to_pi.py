import numpy as np
#import write_output
import cv2

# Grab image from the camera #

vid_cap = cv2.VideoCapture(0)
ret, frame = vid_cap.read()

# convert to gray #

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# get dimensions and create array #

width = int(gray.shape[1])
height = int(gray.shape[0])
bi_array = np.zeros((width * height), dtype=int)

# store frame into array #
print(gray)
print(width)
print(height)

vid_cap.release()