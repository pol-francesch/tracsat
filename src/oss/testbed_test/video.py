import numpy as np
from cv2 import cv2


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

# Gives functionality of ++ and --
class counter(object):
    def __init__(self,v=0):
        self.set(v)

    def preinc(self):
        self.v += 1
        return self.v
    def predec(self):
        self.v -= 1
        return self.v

    def postinc(self):
        self.v += 1
        return self.v - 1
    def postdec(self):
        self.v -= 1
        return self.v + 1

    def __add__(self,addend):
        return self.v + addend
    def __sub__(self,subtrahend):
        return self.v - subtrahend
    def __mul__(self,multiplier):
        return self.v * multiplier
    def __div__(self,divisor):
        return self.v / divisor

    def __getitem__(self):
        return self.v

    def __str__(self):
        return str(self.v)

    def set(self,v):
        if type(v) != int:
            v = 0
        self.v = v

class Video:
    # scale_percent: percent of original size of frame
    def __init__(self, dim=(640,480), color='8bit'):
        self.cap = cv2.VideoCapture(0)
        self.dim = dim
        self.oldFrame = False
        self.color = color
    
    def getFrame(self):
        _, frame = self.cap.read()

        frame = cv2.resize(frame, self.dim, interpolation=cv2.INTER_AREA)

        # Switch frame to greyscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray
    
    def getFrameBits(self):
        frame = self.getFrame()
        frame_bits = [intToBits(pixel) for row in frame for pixel in row]

        # for row in frame:
        #     for pixel in row:
        #         frame_bits.append(intToBits(pixel))
        
        return frame_bits
    
    def getFrameBitsFast(self):
        frame = self.getFrame()
        
        if self.color == '8bit':
            frame_bits = np.unpackbits(frame)
        elif self.color == '4bit':
            frame = np.vstack(np.remainder(frame, 16).flatten())
            frame_bits = np.unpackbits(frame, axis=1, bitorder='big').flatten()

        return frame_bits
    
    def getFrameBitCompressed(self):
        frame = self.getFrame()

        # First check if this is the first frame
        if type(self.oldFrame) is bool:
            self.oldFrame = frame
            return np.concatenate(([0], binary_repr(frame)))
        
        # Compress
        updateMatrix = ~np.equal(frame, self.oldFrame)*1
        updatePixels = np.multiply(frame, updateMatrix).flatten()
        updateMatrix = updateMatrix.flatten()
        updatePixels = updatePixels[updatePixels != 0].astype(np.uint8)
        updateBits = np.unpackbits(updatePixels)

        bigDaddy = np.concatenate((updateMatrix, updateBits))
        self.oldFrame = frame

        # Check which is smaller
        send = np.concatenate(([1],bigDaddy)) if bigDaddy.shape[0] < frame.shape[0]*frame.shape[1]*8 else np.concatenate(([0],np.unpackbits(frame)))

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
    
    def getFrameBitToInt(self, frame, compressed=False, color='8bit'):
        if not compressed:
            # if color == '4bit':
            #     frame = frame.reshape((self.dim[0]*self.dim[1], 4))
            #     return 16*np.packbits(frame, axis=-1, bitorder='little').reshape((self.dim[1], self.dim[0]))
            
            return 16*np.packbits(frame).reshape((self.dim[1], self.dim[0]))
        else:
            # Check if we sent the compressed version
            if frame[0] == 0:
                return np.packbits(frame[1:]).reshape(self.dim)
            else:
                # Unpack the input
                updateMatrix = frame[1:self.dim[0]*self.dim[1]+1]
                updatePixels = np.packbits(frame[self.dim[0]*self.dim[1]+1:])

                # Convert to int
                i = counter()
                updateMatrixInt = np.where(updateMatrix == 1, updatePixels[i.postinc()], updateMatrix).reshape((self.dim[1], self.dim[0]))
                
                # Get the non-updated old frame
                nonUpdated = np.multiply(~updateMatrix.reshape((self.dim[1], self.dim[0])), self.oldFrame)

                # Return output
                ret = updateMatrixInt + nonUpdated

                return ret
    
    def countSlow(self, frame):
        count = 0
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                count = count + int(frame[i][j] != self.oldFrame[i][j])
        
        print(count)


if __name__ == '__main__':
    video = Video(color='8bit')
    frame8 = video.getFrameBitsFast()
    print(frame8.shape)
    print(frame8[0:16])

    video.setColor('4bit')
    frame4 = video.getFrameBitsFast()
    print(frame4.shape)
    print(frame4[0:16])
    # print(frame)