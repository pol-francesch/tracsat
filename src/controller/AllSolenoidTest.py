import math
import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_bno055

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

posX = 17
negX = 27
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

GPIO.output(posX, GPIO.HIGH)
time.sleep(1)
GPIO.output(negX, GPIO.HIGH)
time.sleep(1)
GPIO.output(posY, GPIO.HIGH)
time.sleep(1)
GPIO.output(negY, GPIO.HIGH)
time.sleep(1)
GPIO.output(posZ, GPIO.HIGH)
time.sleep(1)
GPIO.output(negZ, GPIO.HIGH)
time.sleep(5)

GPIO.output(posX, GPIO.LOW)
GPIO.output(negX, GPIO.LOW)
GPIO.output(posY, GPIO.LOW)
GPIO.output(negY, GPIO.LOW)
GPIO.output(posZ, GPIO.LOW)
GPIO.output(negZ, GPIO.LOW)
