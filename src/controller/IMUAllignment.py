#from scipy.ndimage import gaussian_filter1d
import numpy as np
import math
import time
import board
import busio
import adafruit_bno055
import controller
import serial
#import RPi.GPIO as GPIO

i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = adafruit_bno055.BNO055_I2C(i2c)

uart = serial.Serial("/dev/serial0")
sensor2 = adafruit_bno055.BNO055_UART(uart)

while True:
    magX1, magY1, magZ1 = sensor1.magnetic
    magX2, magY2, magZ2 = sensor2.magnetic

    heading1 = math.atan2(magY1, magX1) * 180 / math.pi
    heading2 = math.atan2(magY2, magX2) * 180 / math.pi

    print(abs(heading1-heading2))
