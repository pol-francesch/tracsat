import numpy as np
from cv2 import cv2
import timeit


def intToBits(x):
    send = str(bin(x).lstrip('0b'))
    send = send.zfill(8)

    return send

def binary_repr(x):
    return (
        np.dstack((
            np.bitwise_and(x, 0b10000000) >> 7,
            np.bitwise_and(x, 0b1000000) >> 6,
            np.bitwise_and(x, 0b100000) >> 5,
            np.bitwise_and(x, 0b10000) >> 4,
            np.bitwise_and(x, 0b1000) >> 3,
            np.bitwise_and(x, 0b100) >> 2,
            np.bitwise_and(x, 0b10) >> 1,
            np.bitwise_and(x, 0b1)
        )). flatten() > 0
    )

class Video:
    # scale_percent: percent of original size of frame
    def __init__(self, dim=(640,480), color='8bit', compression=False):
        self.cap = cv2.VideoCapture(1)
        # self.cap = cv2.VideoCapture(0)
        self.dim = dim
        self.oldFrame = False
        self.color = color
        self.compression = compression

    def getFrame(self):
        _, frame = self.cap.read()

        frame = cv2.resize(frame, self.dim, interpolation=cv2.INTER_AREA)

        # Switch frame to greyscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray

    def getFrameBits(self):
        frame = self.getFrame()

        if self.compression:
            frame_bits = self.getFrameBitCompressed()
        else:
            frame_bits = self.getFrameBitsFast()

        return frame_bits

    def getFrameBitsFast(self):
        frame = self.getFrame()

        if self.color == '8bit':
            frame_bits = np.unpackbits(frame)
        elif self.color == '4bit':
            frame = frame.reshape((-1,1))
            frame = ((frame - np.remainder(frame, 16))/16).astype(np.uint8)
            frame_bits = np.unpackbits(frame, bitorder='little', count=4, axis=1)

        return frame_bits

    def getFrameBitCompressed(self):
        frame = self.getFrame()

        if self.color == '8bit':
            # First check if this is the first frame
            if type(self.oldFrame) is bool:
                self.oldFrame = frame
                return np.concatenate(([0], np.unpackbits(frame)))

            # Compress
            dummy = np.where(frame==0, 1, frame)
            updateMatrix = ~np.equal(dummy, self.oldFrame)*1
            updatePixels = np.multiply(dummy, updateMatrix).flatten()
            updateMatrix = updateMatrix.flatten()
            updatePixels = updatePixels[updatePixels != 0].astype(np.uint8)
            updateBits = np.unpackbits(updatePixels)

            bigDaddy = np.concatenate((updateMatrix, updateBits))
            self.oldFrame = frame

            # Check which is smaller
            send = np.concatenate(([1],bigDaddy)) if bigDaddy.shape[0] < frame.shape[0]*frame.shape[1]*8 else np.concatenate(([0],np.unpackbits(frame)))

            return send

        elif self.color == '4bit':
            # Change to 4bit
            frame = frame.reshape((-1,1))
            frame = ((frame - np.remainder(frame, 16))/16).astype(np.uint8)

            # First check if this is the first frame
            if type(self.oldFrame) is bool:
                self.oldFrame = frame
                ret = np.concatenate(([0], np.unpackbits(frame, axis=-1, bitorder='little', count=4).flatten()))
                return ret

            # Compress
            dummy = np.where(frame==0, 1, frame)
            updateMatrix = ~np.equal(dummy, self.oldFrame)*1
            updatePixels = np.multiply(dummy, updateMatrix)

            #updateMatrix = updateMatrix.flatten()
            updateMatrix = updateMatrix.reshape((-1,1))
            updatePixels = ((updatePixels - np.remainder(updatePixels, 16))/16).astype(np.uint8)
            #updatePixels = updatePixels[updatePixels != 0].astype(np.uint8)
            updateBits = np.unpackbits(updatePixels, bitorder='little', count=1, axis=-1)
            #print(updateMatrix)
            #print(updateBits)
            #updatePixels = np.vstack(updatePixels[updatePixels != 0].astype(np.uint8).flatten())
            #updateBits = np.unpackbits(updatePixels, axis=-1, bitorder='little', count=4).flatten()
            print(updateMatrix)
            print(updateBits)
            bigDaddy = np.concatenate((updateMatrix, updateBits))
            self.oldFrame = frame

            # Check which is smaller
            send = np.concatenate(([1],bigDaddy)) if bigDaddy.shape[0] < frame.shape[0]*frame.shape[1]*8 else np.concatenate(([0],np.unpackbits(frame, axis=-1, bitorder='little', count=4).flatten()))

            return send

    def __del__(self):
        self.cap.release()

    def setFPS(self, fps):
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def setDim(self, dim):
        self.dim = dim
        self.oldFrame = False
        print(self.dim)

    def setColor(self, color):
        self.color = color
        self.oldFrame = False

    def countSlow(self, frame):
        count = 0
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                count = count + int(frame[i][j] != self.oldFrame[i][j])

        print(count)

class ShowVideo:
    # scale_percent: percent of original size of frame
    def __init__(self, dim=(640,480), color='8bit', compression=False):
        self.cap = cv2.VideoCapture(1)
        # self.cap = cv2.VideoCapture(0)
        self.dim = dim
        self.oldFrame = False
        self.color = color
        self.compression = compression

    def getFrameBitToInt(self, frame_bits):
        if not self.compression:
            if self.color == '4bit':
                frame = frame_bits.reshape((self.dim[0]*self.dim[1], 4))
                return 16*np.packbits(frame, axis=-1, bitorder='little').reshape((self.dim[1], self.dim[0]))

            return np.packbits(frame_bits).reshape((self.dim[1], self.dim[0]))
        else:
            if self.color == '8bit':
                # Check if we sent the compressed version
                if frame_bits[0] == 0 or type(self.oldFrame) is bool:
                    frame = np.packbits(frame_bits[1:]).reshape((self.dim[1], self.dim[0]))
                    self.oldFrame = frame
                    return frame
                else:
                    # Unpack the input
                    updateMatrix = frame_bits[1:self.dim[0]*self.dim[1]+1]
                    updatePixels = np.packbits(frame_bits[self.dim[0]*self.dim[1]+1:])

                    # Convert to int
                    updateMatrixInt = np.zeros((self.dim[0]*self.dim[1],1))
                    countb = 0

                    for i in range(self.dim[0]*self.dim[1]):
                        if updateMatrix[i] == 1:
                            updateMatrixInt[i] = updatePixels[countb]
                            countb += 1

                    updateMatrixInt = updateMatrixInt.flatten().astype(np.uint8).reshape((self.dim[1], self.dim[0]))

                    # Get the non-updated old frame
                    nonUpdateMatrix = np.where(updateMatrix == 1, 0, 1)
                    nonUpdated = np.multiply(nonUpdateMatrix.reshape((self.dim[1], self.dim[0])), self.oldFrame)

                    # Return output
                    ret = np.asarray(updateMatrixInt + nonUpdated, dtype=np.uint8)
                    self.oldFrame = ret

                    return ret
            elif self.color == '4bit':
                # Check if we sent the compressed version
                if frame_bits[0] == 0 or type(self.oldFrame) is bool:
                    frame = frame_bits[1:].reshape((self.dim[0]*self.dim[1], 4))
                    gray = 16*np.packbits(frame, axis=-1, bitorder='little').reshape((self.dim[1], self.dim[0]))
                    self.oldFrame = gray
                    return gray
                else:
                    # Unpack the input
                    updateMatrix = frame_bits[1:self.dim[0]*self.dim[1]+1]
                    frame = frame_bits[self.dim[0]*self.dim[1]+1:].reshape((-1, 4))
                    updatePixels = 16*np.packbits(frame, axis=-1, bitorder='little')

                    # Convert to int
                    updateMatrixInt = np.zeros((self.dim[0]*self.dim[1],1))
                    countb = 0

                    for i in range(self.dim[0]*self.dim[1]):
                        if updateMatrix[i] == 1:
                            updateMatrixInt[i] = updatePixels[countb]
                            countb += 1

                    updateMatrixInt = updateMatrixInt.flatten().astype(np.uint8).reshape((self.dim[1], self.dim[0]))

                    # Get the non-updated old frame
                    nonUpdateMatrix = np.where(updateMatrix == 1, 0, 1)
                    nonUpdated = np.multiply(nonUpdateMatrix.reshape((self.dim[1], self.dim[0])), self.oldFrame)

                    # Return output
                    ret = np.asarray(updateMatrixInt + nonUpdated, dtype=np.uint8)
                    self.oldFrame = ret

                    return ret

    def setDim(self, dim):
        self.dim = dim
        self.oldFrame = False
        print(self.dim)

    def setColor(self, color):
        self.color = color
        self.oldFrame = False

if __name__ == '__main__':
    start = timeit.default_timer()
    video = Video(color='4bit', compression=True)
    showVideo = ShowVideo(color='4bit', compression=True)
    frame_bits = video.getFrameBits()
    gray       = showVideo.getFrameBitToInt(frame_bits)
    print(gray)
    stop = timeit.default_timer()
    print("Time: ", stop - start)

    while (True):
        frame_bits = video.getFrameBits()
        gray = showVideo.getFrameBitToInt(frame_bits)
        cv2.imshow('TracSat', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    showVideo.cap.release()
    cv2.destroyAllWindows()
