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

class Video:
    # scale_percent: percent of original size of frame
    def __init__(self, dim=(640,480)):
        self.cap = cv2.VideoCapture(0)
        self.dim = dim
        self.oldFrame = False
    
    # color: If true show color frames. Not yet implemented
    def getFrame(self, color=False):
        _, frame = self.cap.read()

        frame = cv2.resize(frame, self.dim, interpolation=cv2.INTER_AREA)

        if not color:
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
        frame_bits = binary_repr(frame)

        return frame_bits
    
    def getFrameBitCompressed(self):
        frame = self.getFrame()

        # First check if this is the first frame
        if type(self.oldFrame) is bool:
            self.oldFrame = frame
            return binary_repr(frame)
        
        # Compress
        updateMatrix = ~np.equal(frame, self.oldFrame)*1
        updatePixels = np.multiply(frame, updateMatrix).flatten()
        updateMatrix = updateMatrix.flatten()
        updatePixels = updatePixels[updatePixels != 0]
        updateBits = binary_repr(updatePixels)*1

        bigDaddy = np.concatenate((updateMatrix, updateBits))
        self.oldFrame = frame

        # Check which is smaller
        send = bigDaddy if bigDaddy.shape[0] < frame.shape[0]*frame.shape[1] else frame

        return send        

    def __del__(self):
        self.cap.release()

    def getVideo(self, color=False):
        while True:
            frame = self.getFrame(color=color)

            cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)

            cv2.imshow('TracSat', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
    
    def setFPS(self, fps):
        self.cap.set(cv2.CAP_PROP_FPS, fps)
    
    def setDim(self, dim):
        self.dim = dim
        self.oldFrame = False
        print(self.dim)


if __name__ == '__main__':
    video = Video()

    _ = video.getFrameBitCompressed()
    _ = video.getFrameBitCompressed()
    # print(frame)