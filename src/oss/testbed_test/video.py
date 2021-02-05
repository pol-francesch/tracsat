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
    def __init__(self, scale_percent=100):
        self.cap = cv2.VideoCapture(0)

        # Get one frame to figure out sizing contraints
        _, frame = self.cap.read()

        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        self.dim = (width, height)
    
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

        for row in frame:
            for pixel in row:
                frame_bits.append(intToBits(pixel))
        
        return frame_bits
    
    def getFrameBitsFast(self):
        frame = self.getFrame()
        frame_bits = binary_repr(frame)

        return frame_bits
    
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


if __name__ == '__main__':
    video = Video(scale_percent=100)

    frame = video.getFrameBits()

    print(frame)