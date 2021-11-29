import numpy as np
import cv2

# Getting video
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0)

# Setting FPS
# cap.set(cv2.CAP_PROP_FPS, 1)

# Get one frame to figure out sizing contraints
ret, frame = cap.read()

scale_percent = 100          # percent of original size
width = int(frame.shape[1] * scale_percent / 100)
height = int(frame.shape[0] * scale_percent / 100)
dim = (width, height)

while(True):    
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Resize frame
    # frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("TracSat", 1000, 1000)

    cv2.imshow('TracSat', gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Look at frame sizing
print("Frame shape", frame.shape)
print("Frame array value: ", type(frame[0][0][0]))
print("Gray shape: ", gray.shape)
print("Gray array value: ", type(gray[0][0]))

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()