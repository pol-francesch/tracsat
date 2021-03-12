from cv2 import cv2
import sys

from video import Video, ShowVideo

def overlayText(color='8bit', compression=False):
    # Create picture
    cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("TracSat", 640*2, 480*2)

    # Init Video class
    video = Video(color=color)
    showVideo = ShowVideo(color=color, compression=compression)

    while(True):
        try:
            # Capture frame-by-frame
            # Transfer frame to bits
            if compression:
                frame_bits = video.getFrameBitCompressed()
            else:
                frame_bits = video.getFrameBitsFast()
            
            # Trasnfer frame back to int
            gray = showVideo.getFrameBitToInt(frame_bits)

            # Add text to image
            # Documentation: https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/
            # Note: The input must be a string
            # Try to reduce the number of times you do image = cv2.putText(...)
            # Maybe if you can figure out how to have multiple lines in a single input? (So you would do the operation once
            # and the text gets split up into different lines)
            image = cv2.putText(gray, 'TracSat', (50,50), cv2.FONT_HERSHEY_COMPLEX, 
                        1, (255,0,0), 2, cv2.LINE_AA)

            someNumber = 20
            image2 = cv2.putText(image, str(someNumber), (60,200), cv2.FONT_HERSHEY_COMPLEX, 
                        1, (255,0,0), 2, cv2.LINE_AA)

            # Display the resulting frame            
            cv2.imshow('TracSat', image2)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print(gray)
            raise


if __name__ == '__main__':
    overlayText(color="8bit", compression=True)