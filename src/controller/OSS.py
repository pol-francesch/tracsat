#from scipy.ndimage import gaussian_filter1d
import numpy as np
import math
import time
#import board
#import busio
#import adafruit_bno055
import controller
import RPi.GPIO as GPIO
from oss.testbed_test.lidar import Lidar
#import simulation

#i2c = busio.I2C(board.SCL, board.SDA)
#sensor = adafruit_bno055.BNO055_I2C(i2c)

GPIO.setmode(GPIO.BCM)

posX = 17
negX = 27
posY = 10
negY = 9
posZ = 5
negZ = 6

GPIO.setup(posX, GPIO.OUT)
GPIO.output(posX, GPIO.LOW)

GPIO.setup(negX, GPIO.OUT)
GPIO.output(negX, GPIO.LOW)

GPIO.setup(posY, GPIO.OUT)
GPIO.output(posY, GPIO.LOW)

GPIO.setup(negY, GPIO.OUT)
GPIO.output(negY, GPIO.LOW)

GPIO.setup(posZ, GPIO.OUT)
GPIO.output(posZ, GPIO.LOW)

GPIO.setup(negZ, GPIO.OUT)
GPIO.output(negZ, GPIO.LOW)

directionPins = np.array([posX,negX,posY,negY,posZ,negZ])

fileName = "logFile.txt"

f = open(fileName,"w")

#PATH PLANNING AND OBJECT FINDING HERE

#position of object relative to s/c, assume we have from lidar
xPos = 0
yPos = 0

t0 = time.time()

lidar = Lidar()

[vectorX, vectorY] = lidar.findObject()

t1 = time.time()

objectX = vectorX
objectY = vectorY

distToObject = math.sqrt((objectX)**2+(objectY)**2)

euler1 = math.atan2(objectY,objectX)

#points along path from path planning, assume x is in general direction from tracSat starting point to object
x = np.array([0,.9*math.cos(euler1)])
y = np.array([0,.9*math.sin(euler1)])
#A = np.array([[0,0], [0.5,4], [1.5,5], [1.5,6.5], [.5,7.5], [-.5,7.5], [-1.5,6.5], [-1.5,5], [-.5,4]])
#y, x = A.T

curvatureThreshold = 13

xW,yW = controller.getWaypoints(x,y,curvatureThreshold)

startWaypoint = 0
endWaypoint = 1

phi = math.atan2((yW[endWaypoint]-yW[startWaypoint]),(xW[endWaypoint]-xW[startWaypoint])) #angle of checkpoint line wrt horizontal
if phi < 0:
    phi += 2*math.pi

waypointDist = math.sqrt(((yW[endWaypoint]-yW[startWaypoint])**2+(xW[endWaypoint]-xW[startWaypoint])**2)) #distance between waypoints

thrusters = np.zeros(6)

temp = t0
t0 = t1

rS = waypointDist
currentS = (math.cos(phi)*(xPos - xW[startWaypoint]) + math.sin(phi)*(yPos - yW[startWaypoint]))
errorS = rS - currentS
rR = 0
currentR = -math.sin(phi)*(xPos - xW[startWaypoint]) + math.cos(phi)*(yPos - yW[startWaypoint])
errorR = rR - currentR
#rT = math.atan2((objectY - yPos),(objectX - xPos)) #rotation setpoint
rT = 0
currentT = euler1
errorT = rT - currentT #rotation error

f.write("%t0,t1,rS,currentS,errorS,rR,currentR,errorR,rT,currentT,errorT,xPos,yPos,objectX,objectY,thruster1,thruster2,thruster3,thruster4,thruster5,thruster6\n")
f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(temp,t0,rS,currentS,errorS,rR,currentR,errorR,rT,currentT,errorT,xPos,yPos,objectX,objectY,thrusters[0],thrusters[1],thrusters[2],thrusters[3],thrusters[4],thrusters[5]))
#f.close()

objectPos = np.array([objectX, objectY])
satPos = np.array([xPos,yPos])

integrals = np.array([0,0,0])

gains = np.array([[2,0,10],[2,0,10],[2,5,10]]) #[[KpS,KdS,KiS],[KpR,KdR,KiR],[KpT,KdT,KiT]]

prevErrors = np.array([errorS,errorR,errorT])

waypointEdges = np.array([startWaypoint,endWaypoint])

keepRunning = 1

while keepRunning == 1:
    thrusters,satPos,integrals,prevErrors,waypointEdges,t0,keepRunning = controller.pid(objectPos,satPos,integrals,gains,prevErrors,xW,yW,waypointEdges,t0,f,lidar)

    if thrusters[0] == 1:
         GPIO.output(posX, GPIO.HIGH)
    else:
         GPIO.output(posX, GPIO.LOW)

    if thrusters[1] == 1:
        GPIO.output(negX, GPIO.HIGH)
    else:
        GPIO.output(negX, GPIO.LOW)

    if thrusters[2] == 1:
        GPIO.output(posY, GPIO.HIGH)
    else:
        GPIO.output(posY, GPIO.LOW)

    if thrusters[3] == 1:
        GPIO.output(negY, GPIO.HIGH)
    else:
        GPIO.output(negY, GPIO.LOW)

    if thrusters[4] == 1:
        GPIO.output(posZ, GPIO.HIGH)
    else:
        GPIO.output(posZ, GPIO.LOW)

    if thrusters[5] == 1:
        GPIO.output(negZ, GPIO.HIGH)
    else:
        GPIO.output(negZ, GPIO.LOW)

    time.sleep(.05) #wait for solenoids to fully open/close
f.close()
