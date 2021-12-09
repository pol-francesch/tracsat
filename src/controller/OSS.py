import sys
sys.path.append('../')

#from scipy.ndimage import gaussian_filter1d
import numpy as np
import math
import time
#import board
#import busio
#import adafruit_bno055
import controller
import RPi.GPIO as GPIO
from lidar import Lidar
#from src.oss.testbed_test.lidar import Lidar
from datetime import datetime
#import simulation

#i2c = busio.I2C(board.SCL, board.SDA)
#sensor = adafruit_bno055.BNO055_I2C(i2c)

# datetime object containing current date and time
now = str(datetime.now())
now = now.replace(":","_")
now = now.replace("-","_")
now = now.replace(" ","__")
fileName = "/home/pi/tracsat/src/controller/logFile" + now + ".txt"

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

#PATH PLANNING AND OBJECT FINDING HERE

#position of object relative to s/c, assume we have from lidar
xPos = 0
yPos = 0

t0 = time.time()
startTime = t0

lidar = Lidar()

[vectorX, vectorY] = lidar.findObject()

t1 = time.time()

objectX = vectorX
objectY = vectorY

distToObject = math.sqrt((objectX)**2+(objectY)**2)

euler1 = math.atan2(objectY,objectX)

#points along path from path planning, assume x is in general direction from tracSat starting point to object
x = np.array([0,.75*math.cos(euler1)])
y = np.array([0,.75*math.sin(euler1)])
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

outputVec = np.array([temp,t0,rS,currentS,errorS,rR,currentR,errorR,rT,currentT,errorT,xPos,yPos,objectX,objectY,thrusters[0],thrusters[1],thrusters[2],thrusters[3],thrusters[4],thrusters[5]])



#f.close()

objectPos = np.array([objectX, objectY])
satPos = np.array([xPos,yPos])

integrals = np.array([0,0,0])

gains = np.array([[2,0,10],[2,0,10],[2,5,10]]) #[[KpS,KdS,KiS],[KpR,KdR,KiR],[KpT,KdT,KiT]]

prevErrors = np.array([errorS,errorR,errorT])

waypointEdges = np.array([startWaypoint,endWaypoint])

keepRunning = 1
startT = time.time()

while keepRunning == 1 and (time.time() - startT) < 60:
    thrusters,satPos,integrals,prevErrors,waypointEdges,t0,keepRunning,outputVec = controller.pid(objectPos,satPos,integrals,gains,prevErrors,xW,yW,waypointEdges,t0,outputVec,lidar)

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

GPIO.output(posX, GPIO.LOW)
GPIO.output(negX, GPIO.LOW)
GPIO.output(posY, GPIO.LOW)
GPIO.output(negY, GPIO.LOW)
GPIO.output(posZ, GPIO.LOW)
GPIO.output(negZ, GPIO.LOW)

f = open(fileName,"w")

f.write("%t0,t1,rS,currentS,errorS,rR,currentR,errorR,rT,currentT,errorT,xPos,yPos,objectX,objectY,thruster1,thruster2,thruster3,thruster4,thruster5,thruster6\n")
for i in range(0,len(outputVec)):
    f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(outputVec[i][0],outputVec[i][1],outputVec[i][2],outputVec[i][3],outputVec[i][4],outputVec[i][5],outputVec[i][6],outputVec[i][7],outputVec[i][8],outputVec[i][9],outputVec[i][10],outputVec[i][11],outputVec[i][12],outputVec[i][13],outputVec[i][14],outputVec[i][15],outputVec[i][16],outputVec[i][17],outputVec[i][18],outputVec[i][19],outputVec[i][20]))

f.close()

GPIO.output(posX, GPIO.HIGH)
GPIO.output(negX, GPIO.HIGH)
GPIO.output(posY, GPIO.HIGH)
GPIO.output(negY, GPIO.HIGH)
GPIO.output(posZ, GPIO.HIGH)
GPIO.output(negZ, GPIO.HIGH)
time.sleep(.5)
GPIO.output(posX, GPIO.LOW)
GPIO.output(negX, GPIO.LOW)
GPIO.output(posY, GPIO.LOW)
GPIO.output(negY, GPIO.LOW)
GPIO.output(posZ, GPIO.LOW)
GPIO.output(negZ, GPIO.LOW)
time.sleep(.5)
GPIO.output(posX, GPIO.HIGH)
GPIO.output(negX, GPIO.HIGH)
GPIO.output(posY, GPIO.HIGH)
GPIO.output(negY, GPIO.HIGH)
GPIO.output(posZ, GPIO.HIGH)
GPIO.output(negZ, GPIO.HIGH)
time.sleep(.5)
GPIO.output(posX, GPIO.LOW)
GPIO.output(negX, GPIO.LOW)
GPIO.output(posY, GPIO.LOW)
GPIO.output(negY, GPIO.LOW)
GPIO.output(posZ, GPIO.LOW)
GPIO.output(negZ, GPIO.LOW)
time.sleep(.5)
GPIO.output(posX, GPIO.HIGH)
GPIO.output(negX, GPIO.HIGH)
GPIO.output(posY, GPIO.HIGH)
GPIO.output(negY, GPIO.HIGH)
GPIO.output(posZ, GPIO.HIGH)
GPIO.output(negZ, GPIO.HIGH)
time.sleep(.5)
GPIO.output(posX, GPIO.LOW)
GPIO.output(negX, GPIO.LOW)
GPIO.output(posY, GPIO.LOW)
GPIO.output(negY, GPIO.LOW)
GPIO.output(posZ, GPIO.LOW)
GPIO.output(negZ, GPIO.LOW)
time.sleep(.5)
