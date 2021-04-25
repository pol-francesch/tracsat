import numpy as np 
# import matplotlib.pyplot as plt
from cv2 import cv2
import sys

from video import Video, ShowVideo
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
# def compareImageAndUpdate():
#     # Set up givens
#     laserBaud = 50000
#     compressionFixed = 0.5
#     compressionVariable = 1e-30

#     # Set up arrays
#     imageSizes   = [(640, 480), (480, 360), (320, 240), (160, 120)]
#     updateValues = np.linspace(0.0, 1.0, num=100, endpoint=True)
#     compressionTimes = np.zeros((4, 100))

#     # Get values
#     for imageSize, i in zip(imageSizes, range(4)):
#         for updateValue, j in zip(updateValues, range(100)):
#             compressionTimes[i][j] = compression_time(imageSize, laserBaud, compressionFixed, compressionVariable, updateValue)

#     # Plot the different shapes
#     for i in range(4):
#         plt.plot(updateValues, compressionTimes[i], label=str(imageSizes[i]))
    
#     plt.legend(fontsize=14)
#     plt.xlabel('Pixels that Need to be Updated / Total Number of Pixels', fontsize=16)
#     plt.ylabel('Amount of Time to Capture Frame and be Ready to Show at GS (s)', fontsize=16)
#     plt.title('How does a Videos\' Characteristics Affect the Time to Show it at the Ground Station?', fontsize=18)
#     plt.show()

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
    showVideoNo = ShowVideo(dim=imageSizes[0],color=color, compression=False)
    showVideo   = ShowVideo(dim=imageSizes[0],color=color, compression=True)

    # We will want to run this for 100 iterations.
    # Will run each separately
    # First run the normal video time (no compression)
    for i in range(4):
        video.setDim(imageSizes[i])
        showVideoNo.setDim(imageSizes[i])
        timeSend = 0

        t_start = time.time()
        for _ in range(iterations):
            frame = video.getFrameBitsFast()

            # Need to add in sending time here
            timeSend = timeSend + frame.shape[0]/laserBaud
            avgShape[0][i] = avgShape[0][i] + frame.shape[0]

            # Decompression
            # _ = showVideoNo.getFrameBitToInt(frame)
        
        # Get time to have frame ready + sending time
        times[0][i] = (time.time() - t_start) / iterations + timeSend / iterations
        avgShape[0][i] = avgShape[0][i]/iterations
    
    # Next run the compressed video time
    for i in range(4):
        video.setDim(imageSizes[i])
        showVideo.setDim(imageSizes[i])
        timeSend = 0

        t_start = time.time()
        for _ in range(iterations):
            frame = video.getFrameBitCompressed()

            # Need to add in sending time here
            timeSend = timeSend + frame.shape[0]/laserBaud
            avgShape[1][i] = avgShape[1][i] + frame.shape[0]

            # Decompression
            # _ = showVideo.getFrameBitToInt(frame)

        
        # Get the average time
        times[1][i] = (time.time() - t_start) / iterations + timeSend / iterations
        avgShape[1][i] = avgShape[1][i]/iterations

    # Plot the different data sets
    print(times)
    print(avgShape)

def compareColor(compression=False):
    # Set up givens
    laserBaud = 50000
    iterations = 50

    # Set up arrays
    imageSizes = [(640, 480), (480, 360), (320, 240), (160, 120)]
    times      = np.zeros((2,4))
    avgShape   = np.zeros((2,4))

    # Set up video
    video = Video(dim=imageSizes[0], color="8bit")
    showVideo   = ShowVideo(dim=imageSizes[0],color="8bit", compression=compression)

    # We will want to run this for 100 iterations.
    # Will run each separately
    # First run the normal video time (no compression)
    for i in range(4):
        video.setDim(imageSizes[i])
        showVideo.setDim(imageSizes[i])
        timeSend = 0

        t_start = time.time()
        for _ in range(iterations):
            if compression:
                frame = video.getFrameBitCompressed()
            else:
                frame = video.getFrameBitsFast()

            # Need to add in sending time here
            timeSend = timeSend + frame.shape[0]/laserBaud
            avgShape[0][i] = avgShape[0][i] + frame.shape[0]

            # Decompression
            _ = showVideo.getFrameBitToInt(frame)
        
        # Get time to have frame ready + sending time
        times[0][i] = (time.time() - t_start) / iterations # + timeSend / iterations
        avgShape[0][i] = avgShape[0][i]/iterations
    
    # Change to 4bit color
    video.setColor("4bit")
    showVideo.setColor("4bit")

    # Next run the 4bit video time
    for i in range(4):
        video.setDim(imageSizes[i])
        showVideo.setDim(imageSizes[i])
        timeSend = 0

        t_start = time.time()
        for _ in range(iterations):
            if compression:
                frame = video.getFrameBitCompressed()
            else:
                frame = video.getFrameBitsFast()

            # Need to add in sending time here
            timeSend = timeSend + frame.shape[0]/laserBaud
            avgShape[1][i] = avgShape[1][i] + frame.shape[0]

            # Decompression
            _ = showVideo.getFrameBitToInt(frame)

        
        # Get the average time
        times[1][i] = (time.time() - t_start) / iterations # + timeSend / iterations
        avgShape[1][i] = avgShape[1][i]/iterations

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

def doesPseudoCompressionWork(color='8bit', compression=False):
    # Create picture
    cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("TracSat", 640*2, 480*2)

    # Init Video class
    video = Video(color=color)
    showVideo = ShowVideo(color=color, compression=compression)

    while(True):
        try:
            # Capture frame-by-frame
            if compression:
                frame_bits = video.getFrameBitCompressed()
            else:
                frame_bits = video.getFrameBitsFast()
            
            gray = showVideo.getFrameBitToInt(frame_bits)

            # Display the resulting frame
            # cv2.imshow('TracSat', gray)

            image = cv2.putText(gray, '60', (50,50), cv2.FONT_HERSHEY_COMPLEX, 
                        1, (255,0,0), 2, cv2.LINE_AA)
            
            cv2.imshow('TracSat', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print(gray)
            raise

def testCompression():
    # Init the video
    cap = cv2.VideoCapture(0)

    # Get the old frame
    _, olFrame = cap.read()
    oldFrame = cv2.resize(olFrame, (640,480), interpolation=cv2.INTER_AREA)
    oldFrame = cv2.cvtColor(oldFrame, cv2.COLOR_BGR2GRAY)

    time.sleep(1)

    # Get the working frame
    _, frame = cap.read()
    frame = cv2.resize(frame, (640,480), interpolation=cv2.INTER_AREA)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Release webcam
    cap.release()

    # Convert the frame back and forth using no compression
    dummy = np.where(frame==0, 1, frame)
    frame_bits_no = np.unpackbits(dummy)

    gray_no = np.packbits(frame_bits_no).reshape((480, 640))

    # Convert the frame back and forth using compression
    # Compression
    dummy = np.where(frame==0, 1, frame)
    updateMatrix = ~np.equal(dummy, oldFrame)*1
    updatePixels = np.multiply(dummy, updateMatrix).flatten()
    updateMatrix = updateMatrix.flatten()
    updatePixels = updatePixels[updatePixels != 0].astype(np.uint8)
    updateBits   = np.unpackbits(updatePixels)

    bigDaddy     = np.concatenate((updateMatrix, updateBits))

    # Decompression
    updateMatrix_d = bigDaddy[0:640*480]
    updateBits_d   = bigDaddy[640*480:]

    # Counter number of updated pixels in both matrices
    print('UpdateMatrix Num Pixels: ' + str(np.count_nonzero(updateMatrix_d == 1)))
    print('UptadeBits Num Pixels: ' + str(updateBits_d.shape[0]/8))

    # Manually check if update matrix is correct
    updateManual = np.zeros((480, 640))

    for i in range(480):
        for j in range(640):
            if oldFrame[i][j] != dummy[i][j]:
                updateManual[i][j] = 1
    
    updateManual = updateManual.flatten().astype(int)
    print('Manual check for the update matrix: ' + str(np.all(updateMatrix_d.astype(int) == updateManual)))

    # Manually check if compression worked
    check_matrix = np.zeros((640*480*8,1))
    oldFrame_bits = np.unpackbits(oldFrame)
    counter1 = np.linspace(0, 480*640, 480*640, endpoint=False).astype(int)
    counter2 = np.linspace(0, 480*640*8, 480*640, endpoint=False).astype(int)
    counterb = 0

    for i,j in zip(counter2, counter1):
        try:
            if updateMatrix_d[j]:
                for k in range(8):
                    check_matrix[i+k] = updateBits[counterb+k].astype(int)
                counterb += 8
            else:
                for k in range(8):
                    check_matrix[i+k] = oldFrame_bits[i+k].astype(int)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print(counterb)
            print(i)
            print(k)
            raise
    check_matrix = check_matrix.flatten().astype(np.uint8)
    print('Check if Compression Matrix Equals no Compression: ' + str(np.all(check_matrix == frame_bits_no)))

    # Perform decompression
    updatePixels = np.packbits(updateBits_d)

    # Convert to int
    updateMatrixIntManual = np.zeros((640*480,1))
    countb = 0

    for i in range(640*480):
        if updateMatrix_d[i] == 1:
            updateMatrixIntManual[i] = updatePixels[countb]
            countb += 1
    
    updateMatrixIntManual = updateMatrixIntManual.flatten().astype(np.uint8)
    
    # Get the non-updated old frame
    nonUpdateMatrix = np.where(updateMatrix_d == 1, 0, 1)
    nonUpdated = np.multiply(nonUpdateMatrix.reshape((480, 640)), oldFrame)

    # Manually get non-updated old frame
    nonUpdatedManual = np.zeros((480*640,1))
    oldFrameFlat = olFrame.flatten()

    for i in range(480*640):
        if updateMatrix_d[i] == 0:
            nonUpdatedManual[i] = oldFrameFlat[i]
        
    nonUpdatedManual = nonUpdatedManual.flatten().astype(np.uint8).reshape((480, 640))
    print(nonUpdatedManual)
    print(nonUpdated)
    print('Check if Non Updated Matrix works: ' + str(np.all(nonUpdated == nonUpdatedManual)))

if __name__ == '__main__':
    comparePseudoCompression(color="4bit")
    # compareColor(compression=False)
    # doesPseudoCompressionWork(color="4bit", compression=True)
    # testCompression()