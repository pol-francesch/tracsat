from scipy.ndimage import gaussian_filter1d
import numpy as np
import math
import time
import board
import busio
import adafruit_bno055
import controller
import RPi.GPIO as GPIO

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

fileName = "log_" + str(round(time.time())) + ".txt"

f = open(fileName,"w")

#PATH PLANNING AND OBJECT FINDING HERE

#position of object relative to s/c, assume we have from lidar
objectX = .5
objectY = .5

#points along path from path planning, assume x is in general direction from tracSat starting point to object
x = np.array([0,1])
y = np.array([0,0])

curvatureThreshold = 13

xW,yW = controller.getWaypoints(x,y,curvatureThreshold)

startWaypoint = 0
endWaypoint = 1

phi = math.atan2((yW[endWaypoint]-yW[startWaypoint]),(xW[endWaypoint]-xW[startWaypoint])) #angle of checkpoint line wrt horizontal
if phi < 0:
    phi += 2*math.pi

waypointDist = math.sqrt(((yW[endWaypoint]-yW[startWaypoint])**2+(xW[endWaypoint]-xW[startWaypoint])**2)) #distance between waypoints

t0 = time.time()

accX, accY, accZ = sensor.linear_acceleration
euler1, euler2, euler3 = sensor.euler

t1 = time.time()

euler1 = euler1 * math.pi/180

xPos, yPos, xVel, yVel = controller.updateKinematics(0,0,0,0,euler1,accX,accY,t0,t1)

t0 = t1

errorS = waypointDist - (math.cos(phi)*(xPos - xW[startWaypoint]) + math.cos(phi)*(yPos - yW[startWaypoint])) #error along path
errorR = -math.sin(phi)*(xPos - xW[startWaypoint]) + math.cos(phi)*(yPos - yW[startWaypoint]) #error perpendicular to path
rT = math.atan2((objectY - yPos),(objectX - xPos)) #rotation setpoint
if rT < 0:
    rT += math.pi*2
errorT = rT - euler1 #rotation error

thrusters = np.zeros(6)

f.write("%t0, xPos, yPos, xVel, yVel, accX, accY, euler1, errorS, errorR, errorT, thruster1, thruster2, thruster3, thruster4, thruster5, thruster6, uS, uR, uT\n")
f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(t0,xPos,yPos,xVel,yVel,accX,accY,euler1,errorS,errorR,errorT,thruster[0],thruster[1],thruster[2],thruster[3],thruster[4],thruster[5],0,0,0))

objectPos = np.array([objectX, objectY])
satPos = np.array([xPos,yPos])
satVel = np.array([xVel,yVel])

integrals = np.array([0,0,0])

gains = np.array([[10,1,.1],[10,1,.1],[10,1,.1]]) #[[KpS,KdS,KiS],[KpR,KdR,KiR],[KpT,KdT,KiT]]

prevErrors = np.array([errorS,errorR,errorT])

waypointEdges = np.array([startWaypoint,endWaypoint])

while True:
    thrusters,satPos,satVel,integrals,prevErrors,waypointEdges,t0 = controller.pid(objectPos,satPos,satVel,integrals,gains,prevErrors,wX,wY,waypointEdges,t0,sensor,f)

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

    time.sleep(.015) #wait for solenoids to fully open/close
