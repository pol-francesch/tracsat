import math
import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_bno055

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

posX = 27
negX = 22
posY = 10
negY = 9
posZ = 5
negZ = 6

GPIO.setup(posX, GPIO.OUT)
GPIO.setup(negX, GPIO.OUT)
GPIO.setup(posY, GPIO.OUT)
GPIO.setup(negY, GPIO.OUT)
GPIO.setup(posZ, GPIO.OUT)
GPIO.setup(negZ, GPIO.OUT)

GPIO.output(posX, GPIO.LOW)
GPIO.output(negX, GPIO.LOW)
GPIO.output(posY, GPIO.LOW)
GPIO.output(negY, GPIO.LOW)
GPIO.output(posZ, GPIO.LOW)
GPIO.output(negZ, GPIO.LOW)

def solTest(pin):
    # for i in range(1,15):
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pin,GPIO.LOW)
    print(pin)

time.sleep(1)
solTest(posX)
time.sleep(1)
solTest(negX)
time.sleep(1)
solTest(posY)
time.sleep(1)
solTest(negY)
time.sleep(1)
solTest(posZ)
time.sleep(1)
solTest(negZ)
time.sleep(1)


