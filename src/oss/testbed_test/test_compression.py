import numpy as np 
import matplotlib.pyplot as plt
from cv2 import cv2

from video import Video
import time

# This function returns the amount of time it would take to from capturing the frame to
# having it ready to display on the other PYNQ given:
# imageSize: The dimension of the image (width, height) in number of pixels
# laserBaud: The frequency of transmission of the laser (Hz)
# compressionFixed: The fixed time of compression + decompression
# compressionVariable: The seconds per pixel of compression and decompression (average)
# update: Updated pixels / total pixels
def compression_time(imageSize, laserBaud, compressionFixed, compressionVariable, update):
    # Include the fixed time first
    totalTime = compressionFixed

    # Include the variable time next (for compression)
    totalPixels = imageSize[0] * imageSize[1]
    updatedPixels = totalPixels * update
    totalTime = totalTime + totalPixels*compressionVariable + updatedPixels*compressionVariable
    # Decompression only goes through the updated pixels. Compression needs to go through all of them

    # Now choose between compression and none
    # Only interested in comparing transmission times
                             # Represesnts matrix    # Represents sending the updated pixels
    sendingTimeCompression = totalPixels/laserBaud + updatedPixels/laserBaud*8
    sendingTimeNone        = totalPixels/laserBaud*8

    sendingTime = sendingTimeCompression if sendingTimeCompression < sendingTimeNone else sendingTimeNone
    totalTime = totalTime + sendingTime

    return totalTime

# Will try to see how image characteristics affect the total time from capturing frame to being ready to show it
def compareImageAndUpdate():
    # Set up givens
    laserBaud = 50000
    compressionFixed = 0.5
    compressionVariable = 1e-30

    # Set up arrays
    imageSizes   = [(640, 480), (480, 360), (320, 240), (160, 120)]
    updateValues = np.linspace(0.0, 1.0, num=100, endpoint=True)
    compressionTimes = np.zeros((4, 100))

    # Get values
    for imageSize, i in zip(imageSizes, range(4)):
        for updateValue, j in zip(updateValues, range(100)):
            compressionTimes[i][j] = compression_time(imageSize, laserBaud, compressionFixed, compressionVariable, updateValue)

    # Plot the different shapes
    for i in range(4):
        plt.plot(updateValues, compressionTimes[i], label=str(imageSizes[i]))
    
    plt.legend(fontsize=14)
    plt.xlabel('Pixels that Need to be Updated / Total Number of Pixels', fontsize=16)
    plt.ylabel('Amount of Time to Capture Frame and be Ready to Show at GS (s)', fontsize=16)
    plt.title('How does a Videos\' Characteristics Affect the Time to Show it at the Ground Station?', fontsize=18)
    plt.show()

# This will compare the initial compression time (so at the TracSat) between normal sending and compression
# Let us assume that sampling the time takes the same amount of time, so the relationship will be linear in nature
def comparePseudoCompression(color="8bit"):
    # Set up givens
    laserBaud = 50000
    iterations = 50

    # Set up arrays
    imageSizes = [(640, 480), (480, 360), (320, 240), (160, 120)]
    times      = np.zeros((2,4))
    avgShape   = np.zeros((2,4))

    # Set up video
    video = Video(dim=imageSizes[0], color=color)

    # We will want to run this for 100 iterations.
    # Will run each separately
    # First run the normal video time (no compression)
    for i in range(4):
        video.setDim(imageSizes[i])
        timeSend = 0

        t_start = time.time()
        for _ in range(iterations):
            frame = video.getFrameBitsFast()

            # # Need to add in sending time here
            timeSend = timeSend + frame.shape[0]/laserBaud
            avgShape[0][i] = avgShape[0][i] + frame.shape[0]

            # # Decompression
            _ = video.getFrameBitToInt(frame, compressed=False, color='4bit')
        
        # Get time to have frame ready + sending time
        times[0][i] = (time.time() - t_start) / iterations #+ timeSend / iterations
        avgShape[0][i] = avgShape[0][i]/iterations
    
    # # Next run the compressed video time
    # for i in range(4):
    #     video.setDim(imageSizes[i])
    #     timeSend = 0

    #     t_start = time.time()
    #     for _ in range(iterations):
    #         frame = video.getFrameBitCompressed()

    #         # Need to add in sending time here
    #         timeSend = timeSend + frame.shape[0]/laserBaud
    #         avgShape[1][i] = avgShape[1][i] + frame.shape[0]

    #         # Decompression
    #         _ = video.getFrameBitToInt(frame, compressed=True)

        
    #     # Get the average time
    #     times[1][i] = (time.time() - t_start) / iterations + timeSend / iterations
    #     avgShape[1][i] = avgShape[1][i]/iterations

    # Plot the different data sets
    print(times)
    print(avgShape)

def compareImages(low=False):
    # Get openCV started
    cap = cv2.VideoCapture(0)

    # Create picture
    cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("TracSat", 640*2, 480*2)

    # Now decide which kind of frame to show
    if low:
        while(True):
            # Capture frame-by-frame
            _, frame = cap.read()

            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Reduce to 4-bit
            gray = gray - np.remainder(gray, 16)
            print(gray)

            # Display the resulting frame
            cv2.imshow('TracSat', gray)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        while(True):
            # Capture frame-by-frame
            _, frame = cap.read()

            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the resulting frame
            cv2.imshow('TracSat', gray)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

def doesVideoEvenWork(color='8bit'):
    # Create picture
    cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("TracSat", 640*2, 480*2)

    # Init Video class
    video = Video(color=color)

    while(True):
        # Capture frame-by-frame
        frame = video.getFrameBitsFast()
        gray = video.getFrameBitToInt(frame, compressed=False, color=color)
        print(np.max(gray))

        # Compare to a manual interpretation
        grayM = video.getFrame()
        # Reduce to 4-bit
        grayM = grayM - np.remainder(grayM, 16)
        print(np.max(grayM))

        # Display the resulting frame
        cv2.imshow('TracSat', gray)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    doesVideoEvenWork(color="4bit")
    # compareImages(True)