import numpy as np

import cv2

cap = cv2.VideoCapture(0)

image_path = '/home/pi/Documents/code_files/test_image.png'

while (True):
    ret, frame = cap.read()
    print('Got frame')
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print('Converted to grayscale')
    
    status = cv2.imwrite(image_path, gray)
    
    print('Image written to file-system: ', status)
    
    break
cap.release()
print('finished')
    