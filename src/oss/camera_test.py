import numpy as np
import cv2

cap = cv2.VideoCapture(0)

# Get one frame to figure out sizing contraints
_, frame = cap.read()

scale_percent = 100          # percent of original size
width = int(frame.shape[1] * scale_percent / 100)
height = int(frame.shape[0] * scale_percent / 100)
dim = (width, height)

while(True):    
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Resize frame
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Look at frame sizing
print("Frame shape", frame.shape)
print("Gray shape: ", gray.shape)
print("Gray type: ", type(gray))
print(type(gray[0][0]))


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()